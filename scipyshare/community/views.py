from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext
from django.http import Http404
from django.contrib import messages

from scipyshare.community.models import Tag, TagCategory, TagCache, TagAssignment
from scipyshare.catalog.models import Entry
from scipyshare.community import permissions

def view_tag(request, tag):
    tag = get_object_or_404(Tag, name=tag)
    entries = Entry.objects.filter(tags__tag=tag)
    entries = _paginated(request, entries)
    return render_to_response('community/tag.html',
                              dict(tag=tag, entries=entries))

def assign_tags(request, slug):
    entry = get_object_or_404(Entry, slug=slug)

    permissions.require_can_tag_entry(request.user, entry)

    categories = TagCategory.objects.all()
    active_tags = [x.tag.name for x in entry.tags.all()]
    your_tags = dict([(x.tag.name, x.score) for x in
                      TagAssignment.objects.filter(user=request.user,
                                                   entry=entry)])

    if request.method == 'POST':
        your_new_tags = {}
        print request.POST
        for key in request.POST.iterkeys():
            if key.startswith('tag-'):
                your_new_tags[key[4:]] = 1.0

        for tag, score in your_tags.iteritems():
            if tag not in your_new_tags:
                your_new_tags[tag] = -1.0

        for tag in active_tags:
            if tag not in your_new_tags:
                your_new_tags[tag] = -1.0

        TagAssignment.assign_tags(request.user, entry, your_new_tags)

        messages.add_message(request, messages.INFO,
                             'Tags for "%s" assigned.' % entry.title)

        return redirect('scipyshare.catalog.views.view', slug)
    else:
        pass

    tag_list = []
    for cat in categories:
        sel = dict(name=cat.name, description=cat.description, tags=[])
        tag_list.append(sel)
        for tag in cat.tags.all():
            your_score = your_tags.get(tag.name, None)
            sel['tags'].append(dict(
                name=tag.name,
                your_pos=your_score is not None and your_score > 0,
                your_neg=your_score is not None and your_score < 0,
                shadow=tag.name in active_tags and your_score is None
                ))

    return render_to_response('community/tag_assign.html',
                              dict(entry=entry,
                                   tag_list=tag_list),
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
