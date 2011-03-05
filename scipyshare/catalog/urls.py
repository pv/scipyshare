from django.conf.urls.defaults import *

urlpatterns = patterns('scipyshare.catalog.views',
    (r'^(?P<slug>[a-z0-9-]+)/$', 'view'),
    (r'^(?P<slug>[a-z0-9-]+)/edit/$', 'edit'),
    (r'^(?P<slug>[a-z0-9-]+)/file/(?P<file_name>.+)/$', 'download'),
    (r'^$', 'index'),
)
