from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext
from django.http import Http404

from scipyshare.community.models import Tag, TagCache
from scipyshare.catalog.models import Entry

def view_tag(request, tag):
    tag = get_object_or_404(Tag, name=tag)
    entries = Entry.objects.filter(tags__tag=tag)
    entries = _paginated(request, entries)
    return render_to_response('community/tag.html',
                              dict(tag=tag, entries=entries))

def assign_tags(request, slug):
    entry = get_object_or_404(Entry, slug=slug)

    if request.method == 'POST':
        pass
    else:
        tags = entry.tags.all()

    return render_to_response('community/tag_assign.html',
                              dict(entry=entry, tags=tags),
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
