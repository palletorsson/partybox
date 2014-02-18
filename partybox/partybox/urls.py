
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from filebrowser.sites import site
admin.autodiscover()



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'partybox.views.home', name='home')
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS,
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^', include('apps.publication.urls')),
    url(r'^admin/', include(admin.site.urls)),

)


if settings.DEBUG:
    urlpatterns += patterns('',

         url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
          url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )