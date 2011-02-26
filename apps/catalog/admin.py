from django.contrib import admin
from catalog.models import Tag, EntryType, License, Entry

admin.site.register(Tag)
admin.site.register(EntryType)
admin.site.register(License)
admin.site.register(Entry)
