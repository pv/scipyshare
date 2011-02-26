from django.conf.urls.defaults import *

urlpatterns = patterns('catalog.views',
    ('^(?P<slug>[a-z0-9-]+)/$', 'view'),
)
