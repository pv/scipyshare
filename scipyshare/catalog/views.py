from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext
from django.http import Http404
from django.db import IntegrityError

from scipyshare.catalog.forms import EntryForm, PackageForm, InfoForm, \
     SnippetForm
from scipyshare.catalog.models import Entry, Revision
from scipyshare.filestorage.models import FileSet

def view(request, slug):
    entry = get_object_or_404(Entry, slug=slug)

    revision = entry.revisions.all()[0]

    fileset = None
    snippet = None
    if revision.fileset:
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

    if not entry.files:
        raise Http404()
    if file_name not in entry.files.listdir():
        raise Http404()

    return redirect(entry.files.url(file_name))

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
                                             #owner=request.user
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
# (1) Filling in revision details, POST to (3)
#     [or back to (1) to upload/delete files]
#
# (2) Preview, with submit button, POST to (1) or to (3)
#
# (3) Submission finished, redirect to result page.
#
# The EntryRevision is created only at step (3).  A temporary FileSet
# is created in (1), if necessary, and its ID is kept in the session.
#
#-------------------------------------------------------------------------------

def edit_entry(request, slug):
    entry = get_object_or_404(Entry, slug=slug)

    def _get_fileset(editable=False):
        sets = request.session.get('fileset')
        try:
            return FileSet(name=sets[slug])
        except (FileSet.DoesNotExist, KeyError, TypeError):
            pass

        last_revision = entry.last_revision
        if not editable:
            if last_revision is not None:
                return last_revision.fileset
            else:
                return None

        fs = FileSet.new_temporary()
        request.session['fileset'] = {slug: fs.name}

        if last_revision is not None:
            last_revision.copy_to(fs)

        return fs

    form_cls = dict(package=PackageForm,
                    snippet=SnippetForm,
                    info=InfoForm)[entry.entry_type]

    fileset = _get_fileset()
    if fileset:
        files = fileset.listdir()
    else:
        files = []

    if request.method == 'POST':
        form = form_cls(request.POST, request.FILES, files=files)

        action = {u'Upload files': 'upload',
                  u'Delete selected files': 'delete',
                  u'Preview': 'preview'}.get(request.POST.get('submit'), None)

        if action == 'preview' and form.is_valid():
            pass
        elif action == 'delete':
            form.errors.clear()


            pass
        elif action == 'upload':
            form.errors.clear()
            pass
    else:
        form = form_cls(files=files)

    return render_to_response('catalog/edit.html',
                              dict(entry=entry, form=form),
                              context_instance=RequestContext(request))
