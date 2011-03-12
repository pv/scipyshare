from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext
from django.http import Http404
from django.db import IntegrityError

from scipyshare.catalog.forms import EntryForm, PackageForm, InfoForm, \
     SnippetForm
from scipyshare.catalog.models import Entry, Revision, License
from scipyshare.filestorage.models import FileSet

def view(request, slug):
    entry = get_object_or_404(Entry, slug=slug)

    revision = entry.last_revision
    fileset = None
    snippet = None
    if revision is not None and revision.fileset:
        snippet = revision.fileset.snippet
        if snippet is None:
            fileset = revision.fileset

    return render_to_response('catalog/entry.html',
                              dict(entry=entry,
                                   revision=revision,
                                   snippet=snippet,
                                   fileset=fileset))

def edit(request, slug):
    entry = get_object_or_404(Entry, slug=slug)

    if request.method == "POST":
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect(view, slug=entry.slug)
    else:
        form = EntryForm(instance=entry)

    return render_to_response('catalog/edit.html',
                              dict(entry=entry, form=form),
                              context_instance=RequestContext(request)
                              )

def _paginated(request, queryset):
    paginator = Paginator(queryset, 100)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        return paginator.page(page)
    except (EmptyPage, InvalidPage):
        return paginator.page(paginator.num_pages)

def index(request):
    entries = _paginated(request, Entry.objects.all())
    return render_to_response('catalog/list.html', dict(entries=entries))

def download(request, slug, file_name):
    entry = get_object_or_404(Entry, slug=slug)

    revision = entry.last_revision
    if not revision:
        raise Http404()

    fileset = revision.fileset
    if not fileset:
        raise Http404()

    if file_name not in fileset.listdir():
        raise Http404()

    return redirect(fileset.url(file_name))

#-------------------------------------------------------------------------------
# Creating a new entry (with no revisions)
#-------------------------------------------------------------------------------

def new_entry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                entry = Entry.new_from_title(title=data['title'],
                                             entry_type=data['entry_type'],
                                             owner=request.user
                                             )
                if entry.slug == 'new':
                    raise IntegrityError()
                entry.save()
                return redirect(edit_entry, entry.slug)
            except IntegrityError:
                # duplicate name
                form.errors['title'] = [u'The title is already in use.']
    else:
        form = EntryForm()

    return render_to_response('catalog/new_entry.html',
                              dict(form=form),
                              context_instance=RequestContext(request))

#-------------------------------------------------------------------------------
# Creating a new revision:
#
# Pages:
#
# (1) Filling in revision details, POST to (2)
#     [or back to (1) to upload/delete files]
#
# (2) Preview, with submit button, POST to (1) or to (3)
#
# (3) Submission finished, redirect to result page.
#
# The Revision is created only at step (3).  A temporary FileSet
# is created in (1), if necessary, and its ID is kept in the session.
#
#-------------------------------------------------------------------------------

def _get_fileset(request, entry, editable=False):
    sets = request.session.get('fileset')
    try:
        return FileSet.objects.get(name=sets[entry.slug])
    except (FileSet.DoesNotExist, KeyError, TypeError):
        pass

    last_revision = entry.last_revision
    if not editable:
        if last_revision is not None:
            return last_revision.fileset
        else:
            return None

    fs = FileSet.new_temporary()
    fs.save()
    request.session['fileset'] = {entry.slug: fs.name}
    if last_revision is not None and last_revision.fileset is not None:
        last_revision.fileset.copy_to(fs)

    return fs

def _clear_fileset(request, entry):
    sets = request.session.get('fileset')
    try:
        fs = FileSet.objects.get(name=sets[entry.slug])
    except (FileSet.DoesNotExist, KeyError, TypeError):
        fs = None
    if fs is not None and fs.is_temporary:
        fs.delete()

def edit_entry(request, slug):
    entry = get_object_or_404(Entry, slug=slug)

    if request.method == 'GET':
        _clear_fileset(request, entry)

    form_cls = dict(package=PackageForm,
                    snippet=SnippetForm,
                    info=InfoForm)[entry.entry_type]

    fileset = _get_fileset(request, entry)
    if fileset:
        files = fileset.listdir()
    else:
        files = []

    show_submit = False
    use_uploads = (entry.entry_type == 'package')

    if request.method == 'POST':
        form = form_cls(request.POST, request.FILES, files=files)

        action = {u'Upload files': 'upload',
                  u'Delete selected files': 'delete',
                  u'Preview': 'preview',
                  u'Edit': 'edit',
                  u'Submit': 'submit'}.get(request.POST.get('submit'), None)

        if use_uploads and fileset is None:
            form.errors['upload_file'] = [u'No files uploaded']

        if action == 'preview' and form.is_valid():
            files = _process_file_uploads(request, entry,
                                          request.FILES.getlist('upload_file'))
            show_submit = True
        elif action == 'submit' and form.is_valid():
            _process_entry_submit(request, entry, form.cleaned_data)
            return redirect(view, entry.slug)
        elif use_uploads and action == 'upload':
            files = _process_file_uploads(request, entry,
                                          request.FILES.getlist('upload_file'))
            form.set_files(files)
            form.errors.clear()
        elif use_uploads and action == 'delete':
            files = _process_file_deletes(request, entry,
                                          form.data.getlist('files'))
            form.set_files(files)
            form.errors.clear()
    else:
        data = _get_entry_data(entry)
        form = form_cls(initial=data, files=files)

    return render_to_response('catalog/edit.html',
                              dict(entry=entry, form=form,
                                   show_upload=use_uploads,
                                   show_submit=show_submit),
                              context_instance=RequestContext(request))

def _get_entry_data(entry):
    revision = entry.last_revision
    if not revision:
        return dict()

    if entry.entry_type == 'package':
        return dict(description=revision.description,
                    license=revision.license,
                    author=revision.author,
                    url=revision.url)
    elif entry.entry_type == 'info':
        return dict(description=revision.description,
                    license=revision.license,
                    author=revision.author,
                    url=revision.url,
                    pypi_name=revision.pypi_name)
    elif entry.entry_type == 'snippet':
        if revision.fileset:
            snippet = revision.fileset.snippet
        else:
            snippet = u""
        return dict(description=revision.description,
                    snippet=snippet)

def _process_file_uploads(request, entry, files):
    if not files:
        fileset = _get_fileset(request, entry)
        if fileset:
            return fileset.listdir()
        else:
            return []

    if entry.entry_type == 'package':
        fileset = _get_fileset(request, entry, editable=True)
        for f in files:
            fileset.write_file(f.name, f)
    elif entry.entry_type == 'snippet':
        fileset = _get_fileset(request, entry, editable=True)
        fileset.snippet = files[0].read(65536)
        fileset.save()
    else:
        return []

    return fileset.listdir()

def _process_file_deletes(request, entry, files_to_remove):
    fileset = _get_fileset(request, entry, editable=True)
    files = fileset.listdir()
    for fn in files:
        if fn in files_to_remove:
            fileset.delete_file(fn)
    return fileset.listdir()

def _process_entry_submit(request, entry, data):
    fileset = _get_fileset(request, entry)

    if entry.entry_type == 'package':
        revision = Revision.new_for_package(
            entry=entry,
            change_comment=data['change_comment'],
            created_by=request.user,
            description=data['description'],
            license=data['license'],
            author=data['author'],
            url=data['url'],
            fileset=fileset)
    elif entry.entry_type == 'info':
        revision = Revision.new_for_info(
            entry=entry,
            change_comment=data['change_comment'],
            created_by=request.user,
            description=data['description'],
            license=data['license'],
            author=data['author'],
            url=data['url'],
            pypi_name=data['pypi_name'])
    elif entry.entry_type == 'snippet':
        if data['snippet']:
            if not fileset or not fileset.is_temporary:
                fileset = _get_fileset(request, entry, editable=True)
            fileset.snippet = data['snippet']
            fileset.save()
        revision = Revision.new_for_snippet(
            entry=entry,
            change_comment=data['change_comment'],
            created_by=request.user,
            description=data['description'],
            fileset=fileset,
            license=License.objects.get(slug='public-domain')
            )
    else:
        raise ValueError("unknown entry type %r" % entry.entry_type)

    revision.save()
    _clear_fileset(request, entry)
