# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
import sys

admin.autodiscover()

urlpatterns = patterns('',

    url("^$", direct_to_template, {"template": "base.html"}, name="home"),
#url(r"^$", 'views.home', name="home"),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^settings/', include('livesettings.urls')),
    
    url(r'^is/', include('coop.initiative.urls')),


    (r'^membre/', include('coop.membre.urls')),

    url(r'^tree/$', 'coop_tree.views.process_nav_edition', name='navigation_tree'),
)

if settings.DEBUG or ('test' in sys.argv):
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    )

urlpatterns += patterns('',
    (r'^(?P<url>.*)$', 'coop_page.views.view_page'),
)

# urlpatterns += patterns('',
#    (r'^', include('uriresolve.urls')),
# )

