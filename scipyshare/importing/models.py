import datetime

from django.db import models, transaction
from django.db import IntegrityError

from scipyshare.catalog.models import Entry, Revision
from scipyshare.community.models import Tag, TagAssignment
from scipyshare.importing import pypi
from scipyshare.importing.classifiers import classifiers

class PypiCache(models.Model):
    """
    Cache for PyPi entries

    """

    name = models.CharField(max_length=256,
                            help_text="Name of a package in PyPi",
                            unique=True)
    version = models.CharField(max_length=256,
                               help_text="Package version in PyPi")

    author = models.TextField(null=True)
    author_email = models.TextField(null=True)
    maintainer = models.TextField(null=True)
    maintainer_email = models.TextField(null=True)
    home_page = models.TextField(null=True)
    license = models.TextField(null=True)
    summary = models.TextField(null=True)
    description = models.TextField(null=True)
    keywords = models.TextField(null=True)
    platform = models.TextField(null=True)
    classifiers = models.TextField(null=True)
    project_url = models.TextField(null=True)

    def __str__(self):
        return self.name

    @classmethod
    def fetch_one(cls, name, version, force=False):
        """
        Update the given entry based on data fetched from PyPi
        """
        if not force:
            # if the release is already there, don't try to update it
            try:
                obj = cls.objects.get(name=name, version=version)
                return
            except cls.DoesNotExist:
                pass
        return cls._fetch_one(name, version)

    @classmethod
    @transaction.commit_on_success
    def _fetch_one(cls, name, version):
        info = pypi.get_info(name, version)
        if info:
            try:
                obj = cls.objects.get(name=name)
            except cls.DoesNotExist:
                obj = cls(name=name, version=version)

            for field in ['name', 'version', 'author', 'author_email',
                          'maintainer', 'maintainer_email', 'home_page',
                          'license', 'summary', 'description', 'keywords',
                          'platform', 'project_url']:
                setattr(obj, field, info.get(field))

            obj.classifiers = _join_list(info.get('classifiers'))
            obj.version = version
            obj.save()

    @classmethod
    def fetch_all(cls, display=False, force=False):
        releases = pypi.get_release_list()
        for name, version in sorted(releases):
            if display:
                print name
            cls.fetch_one(name, version, force=force)


class PypiClassifiers(models.Model):
    classifier = models.CharField(max_length=80)
    tags = models.CharField(max_length=256)

class PypiLink(models.Model):
    pypi_entry = models.ForeignKey(PypiCache, unique=True)
    catalog_entry = models.ForeignKey(Entry)
    pypi_version = models.CharField(max_length=256)
    update_from_pypi = models.BooleanField(default=True)

    @classmethod
    @transaction.commit_on_success
    def update_one(cls, pypi_name, force=False):
        try:
            link = PypiLink.objects.get(pypi_entry__name=pypi_name)
            pypi = link.pypi_entry
            entry = link.catalog_entry

            if not force and (not link.update_from_pypi or
                              pypi.version == link.pypi_version):
                # nothing to do
                return
        except cls.DoesNotExist:
            for names in [pypi_name, pypi_name + ' (Pypi)']:
                try:
                    entry = Entry.new_from_title(title=pypi_name,
                                                 entry_type='info',
                                                 owner=None)
                    entry.save()
                    break
                except IntegrityError:
                    pass
            else:
                raise IntegrityError("Failed to add %r from PyPi -- "
                                     "duplicate names?" % pypi_name)

            pypi = PypiCache.objects.get(name=pypi_name)
            link = PypiLink(pypi_entry=pypi, catalog_entry=entry)

        link.pypi_version = pypi.version
        link.save()

        new_description = u""
        new_author = u""
        new_url = None

        if pypi.summary:
            new_description += pypi.summary + u"\n\n"
        if pypi.author:
            new_author += pypi.author
        if pypi.license:
            new_description += u"License: %s\n\n" % pypi.license
        if pypi.description:
            new_description += pypi.description + u"\n\n"
        if pypi.home_page:
            new_url = pypi.home_page

        # Update revision
        revision = entry.last_revision
        if revision is None or revision.created_by is not None:
            # need to create a new revision
            revision = Revision.new_for_info(
                entry, created_by=None, change_comment=u"PyPi import",
                description=new_description, license=None, author=new_author,
                url=pypi.home_page, pypi_name=pypi_name)
        else:
            # only mutate owner-less revisions
            revision.description = new_description
            revision.author = new_author
            revision.url = pypi.home_page
            revision.pypi_name = pypi_name
            revision.created = datetime.datetime.now()
        revision.save()

        # Get tags from classifiers
        tags = {}
        for x in pypi.classifiers.split("\n"):
            x = x.strip()
            tagname = classifiers.get(x)
            if not tagname:
                continue
            try:
                tag = Tag.objects.get(name=tagname)
                tags[tagname] = 1.0
            except Tag.DoesNotExist:
                pass
        TagAssignment.assign_tags(user=None, entry=entry, tags_to_score=tags)


    @classmethod
    def update_all(cls, display=False, force=False):
        for pypi_entry in PypiCache.objects.all():
            if display:
                print pypi_entry.name
            cls.update_one(pypi_entry.name, force=force)

def _join_list(lst, sep="\n"):
    if lst is None:
        return None
    return sep.join(lst)
