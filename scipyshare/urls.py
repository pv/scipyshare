from django.conf.urls.defaults import *

urlpatterns = patterns('scipyshare',
    (r'^tag/(?P<tag>[a-z0-9- ]+)/$', 'community.views.view_tag'),
    (r'^tag/(?P<slug>[a-z0-9- ]+)/assign/$', 'community.views.assign_tags'),
    (r'^catalog/', include('scipyshare.catalog.urls')),
    (r'^user/', include('scipyshare.user.urls')),
    (r'^$', include('scipyshare.front.urls')),
)
