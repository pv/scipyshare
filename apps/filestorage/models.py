from django.db import models
from django.conf import settings

class FileSet(models.Model):
    name = models.CharField(max_length=256, unique=True)
    snippet_contents = models.TextField(null=True)
    # revisions -> [FileRevision]

    @classmethod
    def new_for_title(cls, title):
        """Generate a suitable slug for the given title --- always guaranteed
        to succeed in giving a new unique name for the file set"""
        raise NotImplementedError()

    def get_snippet(self):
        pass
    def set_snippet(self, snip):
        pass
    snippet = property(get_snippet, set_snippet)

    @property
    def files(self):
        raise NotImplementedError()

    def open_file(self, file_name):
        raise NotImplementedError()

    def write_readme(self, text):
        raise NotImplementedError()

class Revision(models.Model):
    version = models.CharField(max_length=50)
    description = models.TextField()
    fileset = models.ForeignKey(FileSet, related_name="revisions")

