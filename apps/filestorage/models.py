import os
import re
import shutil

from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.db.models.signals import pre_delete


class FileSet(models.Model):
    """
    A set of files, stored in a directory named ``name``.

    """

    name = models.CharField(max_length=256, unique=True)
    snippet_contents = models.TextField(null=True)
    # revisions -> [FileRevision]

    @classmethod
    def new_from_title(cls, title, **kw):
        """Generate a suitable slug for the given title --- always guaranteed
        to succeed in giving a new unique name for the file set"""
        name = _sanitize_name(title)
        kw['name'] = os.path.basename(default_storage.get_available_name(
            os.path.join('catalog', name)))
        return cls(**kw)

    def __str__(self):
        return self.name

    def _get_snippet(self):
        return self.snippet_contents
    def _set_snippet(self, snip):
        self.write_file('snippet.py', ContentFile(snip))
        self.snippet_contents = snip
    snippet = property(_get_snippet, _set_snippet)

    def listdir(self):
        try:
            return default_storage.listdir(self.path(''))[1]
        except OSError:
            return []

    def delete(self, file_name):
        default_storage.delete(self.path(file_name))

    def path(self, file_name=''):
        if not file_name:
            return os.path.join('catalog', _sanitize_name(self.name))
        else:
            file_name = _sanitize_name(file_name)
            return os.path.join('catalog', _sanitize_name(self.name), file_name)

    def _delete_all(self):
        path = default_storage.path(self.path())
        if os.path.isdir(path):
            shutil.rmtree(path)

    def url(self, file_name):
        return default_storage.url(self.path(file_name))

    def open(self, file_name, mode='rb'):
        return default_storage.open(self.path(file_name), mode=mode)

    def write_file(self, file_name, content):
        full_path = default_storage.path(self.path(file_name))
        dir_path = os.path.dirname(full_path)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

        f = self.open(file_name, 'wb')
        try:
            for chunk in content.chunks():
                f.write(chunk)
        finally:
            f.close()

        if settings.FILE_UPLOAD_PERMISSIONS is not None:
            os.chmod(full_path, settings.FILE_UPLOAD_PERMISSIONS)

    def write_readme(self, text):
        self.write_file('README.txt', ContentFile(text.encode('utf-8')))

def _deletion_handler(sender, **kwargs):
    if 'instance' in kwargs:
        kwargs['instance']._delete_all()

pre_delete.connect(_deletion_handler, sender=FileSet)

def _sanitize_name(name):
    name = re.sub('[^a-zA-Z0-9-_. ]', '', name).strip()
    name = name.strip('.')
    return os.path.basename(name)
