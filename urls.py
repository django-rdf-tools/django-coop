# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
import sys

# https://code.djangoproject.com/ticket/10405#comment:11
from django.db.models.loading import cache as model_cache
if not model_cache.loaded:
    model_cache.get_models()
    
admin.autodiscover()

if "oembed" in settings.INSTALLED_APPS :
    import oembed
    oembed.autodiscover()

urlpatterns = patterns('',
    url(r'^admin_tools/', include('admin_tools.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    
)

if settings.DEBUG or ('test' in sys.argv):
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    )

urlpatterns += patterns('',
    (r'^', include('coop_geo.urls', app_name='coop_geo')),
    (r'^djaloha/', include('djaloha.urls')),    
    (r'^', include('coop_tag.urls')),
    (r'^', include('coop.urls')),
    (r'^', include('coop_cms.urls')),
    #(r'^', include('uriresolve.urls')),
    
)
