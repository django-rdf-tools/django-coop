# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
import sys

admin.autodiscover()

urlpatterns = patterns('',

    #url("^$", direct_to_template, {"template": "base.html"}, name="home"),
    url(r'^admin_tools/', include('admin_tools.urls')),
    
    url(r'^$', 'coop.views.home', name="home"),

    (r'^chaining/', include('smart_selects.urls')),
    
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^settings/', include('livesettings.urls')),
    
    (r'^perso/$', 'coop.membre.views.perso'),
    (r'^initiative/', include('coop.initiative.urls')),
    (r'^lieu/', include('coop.place.urls')),
    (r'^tag/', include('skosxl.urls')),

    (r'^membre/', include('coop.membre.urls')),

    url(r'^djaloha/aloah-config.js', 'djaloha.views.aloha_config', name='aloha_config'),
    url(r'^cms/tree/$', 'coop_cms.views.process_nav_edition', name='navigation_tree'),
    url(r'^cms/media-library/$', 'coop_cms.views.show_media_library', name='media_library'),
)

if settings.DEBUG or ('test' in sys.argv):
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    )

urlpatterns += patterns('',
    (r'^(?P<url>.*)$', 'coop_cms.views.view_article'),
)

# urlpatterns += patterns('',
#    (r'^', include('uriresolve.urls')),
# )

