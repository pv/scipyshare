from django.conf.urls.defaults import *

urlpatterns = patterns('scipyshare.catalog.views',
    (r'^$', 'index'),
    (r'^new/$', 'new_entry'),
    (r'^(?P<slug>[\w_.-]+)/$', 'view'),
    (r'^(?P<slug>[\w_.-]+)/edit/$', 'edit_entry'),
    (r'^(?P<slug>[\w_.-]+)/file/(?P<file_name>.+)/$', 'download'),
)
