from django.db import models, transaction
from scipyshare.importing import pypi

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


class PypiLink(models.Model):
    pypi_entry = models.ForeignKey(PypiCache)
    update_from_pypi = models.BooleanField(default=True)




def _join_list(lst, sep="\n"):
    if lst is None:
        return None
    return sep.join(lst)
