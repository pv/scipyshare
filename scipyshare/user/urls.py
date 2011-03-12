from django.conf.urls.defaults import *

urlpatterns = patterns('scipyshare.user.views',
    (r'^login/$', 'login_page'),
)
