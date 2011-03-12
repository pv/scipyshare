from django.conf.urls.defaults import *

urlpatterns = patterns('scipyshare.user.views',
    (r'^login/$', 'login_page'),
    (r'^logout/$', 'logout_page'),
)
