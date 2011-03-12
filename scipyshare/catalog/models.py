import re

from django.db import models
from django.contrib.auth.models import User

from scipyshare.filestorage.models import FileSet

class License(models.Model):
    """
    License for the entry
    """

    name = models.CharField(max_length=256,
                            help_text="name for the license")
    slug = models.SlugField(help_text="url slug for the license")

    description = models.TextField(help_text="short-ish description")
    text = models.TextField(help_text="full license text")

    def __str__(self):
        return self.name

    class Meta:
        permissions = (("can_edit", "Can edit this license"),)

class Entry(models.Model):
    """
    Catalog entry (mutable, except for the revision list)
    """
    class Meta:
        ordering = ['slug']

    ENTRY_TYPE_CHOICES = (
        ('package', 'Code package hosted on this site'),
        ('info', 'Reference to a package hosted elsewhere'),
        ('snippet', 'Example code snippet, a cookbook entry, etc.'),
    )

    title = models.CharField(max_length=256)
    slug = models.CharField(max_length=256, unique=True)
    # revisions -> [Revision, ...]

    # Timestamp
    modified = models.DateTimeField(auto_now=True)

    # Just a redirect
    redirect = models.ForeignKey("Entry", null=True)

    # Ownership
    entry_type = models.CharField(max_length=16, choices=ENTRY_TYPE_CHOICES)
    owner = models.ForeignKey(User, related_name="entries", null=True)


    @property
    def last_revision(self):
        try:
            return self.revisions.order_by('-revno')[0]
        except (KeyError, IndexError):
            return None

    # --

    @classmethod
    def new_from_title(cls, title, **kw):
        title = title.strip()
        slug = generate_slug(title)
        kw['slug'] = slug
        return cls(title=title, **kw)

    def __str__(self):
        return self.slug

class Revision(models.Model):
    """
    Revision of the catalog entry data (immutable after creation)

    """
    class Meta:
        unique_together = (("entry", "revno"),)
        order_with_respect_to = "entry"
        ordering = ['-revno']

    # Identifiers
    entry = models.ForeignKey(Entry, related_name="revisions")
    revno = models.PositiveIntegerField()

    # When, by who, and why
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="revisions")
    change_comment = models.TextField()

    # Basic information
    description = models.TextField()
    license = models.ForeignKey(License)
    author = models.CharField(max_length=256)  # Name <email>

    # Source links (home page, PyPi, hosted files)
    url = models.TextField(null=True)
    pypi_name = models.CharField(max_length=256, null=True)
    fileset = models.ForeignKey(FileSet, null=True)

    # --

    @classmethod
    def _get_next_entry_revno(cls, entry):
        last_revision = entry.last_revision
        if last_revision is None:
            return 1
        else:
            return last_revision.revno + 1

    @classmethod
    def new_for_package(cls, entry, created_by, change_comment, description,
                        license, author, url, fileset):
        revno = cls._get_next_entry_revno(entry)
        old_fileset = None
        if fileset.is_temporary:
            old_fileset = fileset
            fileset = FileSet.new_from_slug_and_revision(entry.slug, revno)
            old_fileset.copy_to(fileset)
        revision = cls(entry=entry, revno=revno,
                   created_by=created_by, change_comment=change_comment,
                   description=description, license=license, author=author,
                   url=url)
        if old_fileset is not None:
            fileset.save()
        revision.fileset = fileset
        return revision

    @classmethod
    def new_for_info(cls, entry, created_by, change_comment, description,
                     license, author, url, pypi_name):
        revno = cls._get_next_entry_revno(entry)
        return cls(entry=entry, revno=revno,
                   created_by=created_by, change_comment=change_comment,
                   description=description, license=license, author=author,
                   url=url, pypi_name=pypi_name)

    @classmethod
    def new_for_snippet(cls, entry, created_by, change_comment, description,
                        fileset):
        revno = cls._get_next_entry_revno(entry)
        old_fileset = None
        if fileset.is_temporary:
            old_fileset = fileset
            fileset = FileSet.new_from_slug_and_revision(entry.slug, revno)
            fileset.snippet = old_fileset.snippet
        revision = cls(entry=entry, revno=revno,
                       created_by=created_by, change_comment=change_comment,
                       description=description)
        if old_fileset is not None:
            fileset.save()
        revision.fileset = fileset
        return revision

    def __str__(self):
        return "%s:%d" % (self.entry.slug, self.revno)

def generate_slug(s):
    s = s.strip()
    return re.sub('-+', '-', re.sub(r'[^\w_.-]', '-', s)).lower()
