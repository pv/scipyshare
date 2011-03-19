from django import template
register = template.Library()

from scipyshare.catalog.models import Entry
from scipyshare.community.models import TagCache

@register.inclusion_tag('community/tag_list.html')
def tag_list(entry):
    tags = entry.tags.all()
    return dict(tags=tags)
