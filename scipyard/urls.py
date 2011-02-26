from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^catalog/', include('catalog.urls')),
    (r'^storage/', include('filestorage.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^', include('front.urls')),
)
