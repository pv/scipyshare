from django.contrib import admin
from scipyshare.community.models import Tag, TagCategory, TagAssignment

admin.site.register(Tag)
admin.site.register(TagCategory)
admin.site.register(TagAssignment)
