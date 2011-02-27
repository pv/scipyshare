import re

from django.db import models
from django.contrib.auth.models import User

from filestorage.models import FileSet

class Tag(models.Model):
    name = models.SlugField(unique=True,
                            help_text="name *and* slug for the tag")
    description = models.TextField(help_text="description for the tag")

    def __str__(self):
        return self.name

    class Meta:
        permissions = (("can_edit", "Can edit this tag"),)

class EntryType(models.Model):
    """
    Type of submission. E.g. 'module', 'snippet'
    """
    name = models.CharField(max_length=256, unique=True,
                            help_text="name *and* slug for the tag")
    description = models.TextField(help_text="description for the entry type")

    def __str__(self):
        return self.name

    class Meta:
        permissions = (("can_edit", "Can edit this entry type"),)

class License(models.Model):
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
    title = models.CharField(max_length=256)
    slug = models.CharField(max_length=256, unique=True)

    # Basic information
    description = models.TextField()
    license = models.ForeignKey(License)
    author = models.CharField(max_length=256)  # Name <email>
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    change_comments = models.TextField()

    # Tagging information
    entry_type = models.ForeignKey(EntryType, related_name="entries")
    tags = models.ManyToManyField(Tag, related_name="entries")
    maturity = models.FloatField(help_text="maturity, on scale 0.0-1.0")

    # Source links
    url = models.TextField(null=True)
    pypi_name = models.CharField(max_length=256, null=True)
    files = models.ForeignKey(FileSet, null=True)

    # Ownership
    owners = models.ManyToManyField(User, related_name="entries", null=True)

    @classmethod
    def new_from_title(cls, title, **kw):
        slug = generate_slug(title)
        kw['slug'] = slug
        return cls(title=title, **kw)

    def __str__(self):
        return self.slug

def generate_slug(s):
    s = s.strip()
    return re.sub('-+', '-', re.sub(r'[^\w_.-]', '-', s)).lower()
