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

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    (r'^membre/', include('membre.urls')),

    url(r'^tree/$', 'coop_tree.views.view_tree', name='navigation_tree'),
    url(r'^tree/object-suggest-list/$', 'coop_tree.views.get_object_suggest_list', name='object_suggest_list'),
    url(r'^node/(?P<id>.+)$', 'coop_tree.views.edit_node', name='edit_node'),
)

if settings.DEBUG or ('test' in sys.argv):
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    )

urlpatterns += patterns('',
    (r'^(?P<url>.*)$', 'coop_page.views.view_page'),
)

