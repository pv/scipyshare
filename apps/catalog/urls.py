from django.conf.urls.defaults import *

urlpatterns = patterns('catalog.views',
    ('^$', 'index'),
    ('^#(?P<tag>[a-z0-9-]+)/$', 'view_tag'),
    ('^(?P<slug>[a-z0-9-]+)/$', 'view'),
    ('^(?P<slug>[a-z0-9-]+)/edit/$', 'edit'),
    ('^(?P<slug>[a-z0-9-]+)/file/(?P<file_name>.+)/$', 'download'),
)
