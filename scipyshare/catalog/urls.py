from django.conf.urls.defaults import *

urlpatterns = patterns('scipyshare.catalog.views',
    (r'^$', 'index'),
    (r'^new/$', 'new_entry'),
    (r'^(?P<slug>[a-z0-9-]+)/$', 'view'),
    (r'^(?P<slug>[a-z0-9-]+)/edit/$', 'edit_entry'),
    (r'^(?P<slug>[a-z0-9-]+)/file/(?P<file_name>.+)/$', 'download'),
)
