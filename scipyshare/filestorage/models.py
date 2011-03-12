import os
import re
import shutil

from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile, File
from django.core.exceptions import SuspiciousOperation

from django.db.models.signals import pre_delete

class FileSet(models.Model):
    """
    A set of files, stored in a directory.

    """
    name = models.CharField(max_length=256, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    snippet_contents = models.TextField(null=True)

    @classmethod
    def new_from_slug_and_revision(cls, slug, revision, **kw):
        """
        Generate a file set with a path name corresponding to a given
        slug and revision. Guaranteed to succeed.

        """
        name = os.path.join(_sanitize_name(slug), '%04d' % revision)
        name = default_storage.get_available_name(os.path.join('catalog', name))
        if name.startswith('catalog' + os.path.sep):
            name = name[7+len(os.path.sep):]
        else:
            raise SuspiciousOperation("invalid fileset name from %r:%r" % (
                slug, revision))
        kw['name'] = name
        return cls(**kw)

    @classmethod
    def new_temporary(cls, **kw):
        """
        Generate a file set for temporary use. Guaranteed to succeed.

        """
        name = ",temporary"
        kw['name'] = os.path.basename(default_storage.get_available_name(
            os.path.join('catalog', name)))
        return cls(**kw)

    @property
    def is_temporary(self):
        return self.name.startswith(",temporary")

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
            return default_storage.listdir(self._get_base_path())[1]
        except OSError:
            return []

    def delete_file(self, file_name):
        default_storage.delete(self.path(file_name))

    def _get_base_path(self):
        path = os.path.normpath(os.path.join('catalog', self.name))
        if not path.startswith('catalog' + os.path.sep):
            raise SuspiciousOperation("fileset with invalid name %r"
                                      % self.name)
        return path

    def path(self, file_name=None):
        file_name = _sanitize_name(file_name)
        if not file_name:
            file_name = u'untitled'
        return os.path.join(self._get_base_path(), file_name)

    def _delete_all(self):
        path = default_storage.path(self._get_base_path())
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

    def copy_to(self, other):
        files = self.listdir()
        for fn in files:
            in_f = self.open(fn, 'rb')
            try:
                other.write_file(fn, File(in_f))
            finally:
                in_f.close()

def _deletion_handler(sender, **kwargs):
    if 'instance' in kwargs:
        kwargs['instance']._delete_all()

pre_delete.connect(_deletion_handler, sender=FileSet)

def _sanitize_name(name):
    name = re.sub('[^a-zA-Z0-9-_. ]', '', name).strip()
    name = name.strip('.').strip()
    return os.path.basename(name)
