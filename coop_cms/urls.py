# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^djaloha/aloah-config.js', 'djaloha.views.aloha_init', name='aloha_init'),
    url(r'^cms/tree/$', 'coop_cms.views.process_nav_edition', name='navigation_tree'),
    url(r'^cms/media-library/$', 'coop_cms.views.show_media_library', name='coop_cms_media_library'),
    url(r'^(?P<url>.*)$', 'coop_cms.views.view_article'),
)
