from django.shortcuts import get_object_or_404, render_to_response
from catalog.models import Entry

def view(request, slug):
    entry = get_object_or_404(Entry, slug=slug)
    return render_to_response('catalog/entry.html',
                              dict(entry=entry))

def edit(request, slug):
    entry = get_object_or_404(Entry, slug=slug)
    return render_to_response('catalog/edit.html',
                              dict(entry=entry))
