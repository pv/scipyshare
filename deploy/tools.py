import os

from catalog.models import Entry, License, EntryType, Tag
from filestorage.models import FileSet
from django.core.files.base import ContentFile

def import_dir(dir_name):
    for f in os.listdir(dir_name):
        fn = os.path.join(dir_name, f)
        if os.path.isfile(fn):
            import_file(fn)

def import_file(file_name):
    f = open(file_name, 'rb')
    try:
        data = f.read()
    finally:
        f.close()

    info = {}
    files = {}
    target = None

    lines = data.splitlines(True)
    for line in lines:
        handled = False
        for q in ['title', 'description', 'license', 'author', 'created',
                  'modified', 'change_comments', 'entry_type', 'tags',
                  'maturity', 'url', 'pypi_name', 'pypi']:
            if line.upper().rstrip() == "***" + q.upper():
                target = (info, q)
                handled = True
        if handled:
            continue

        if line.startswith('***FILE:'):
            fn = line[8:].strip()
            if not fn:
                raise ValueError("Invalid file name %s (%s)" % (fn, file_name))
            target = (files, fn)
            continue
        elif line.startswith('***SNIPPET'):
            target = (files, 'snippet.py')
            continue
        else:
            target[0].setdefault(target[1], "")
            target[0][target[1]] += line

    if 'pypi' in info:
        info['pypi_name'] = info.pop('pypi')
    if 'snippet.py' in files:
        info['entry_type'] = 'snippet'

    info.setdefault('entry_type', 'module')
    info.setdefault('license', 'public-domain')
    info.setdefault('maturity', 0.0)

    if 'entry_type' in info:
        info['entry_type'] = EntryType.objects.get(name=info['entry_type'])
    if 'license' in info:
        info['license'] = License.objects.get(slug=info['license'])
    if 'tags' in info:
        info['tags'] = [Tag.objects.get(name=name) for name in
                        [x.strip() for x in info['tags'].split(',')]]

    entry = Entry.new_from_title(**info)
    fileset = FileSet.new_from_title(entry.slug)
    fileset.save()

    entry.files = fileset

    if 'snippet.py' in files:
        fileset.snippet = files['snippet.py']
    else:
        for name, data in files.items():
            fileset.write_file(name, ContentFile(data))

    fileset.save()
    entry.save()
