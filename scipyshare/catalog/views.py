from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext
from django.http import Http404

from scipyshare.catalog.forms import EntryForm
from scipyshare.catalog.models import Entry

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
