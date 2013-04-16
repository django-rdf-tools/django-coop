
# -*- coding:utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^resource/list/$', 'coop.doc.views.resource_list', name='resource-list'),
	url(r'^resource/(?P<slug>[\w-]+)/$', 'coop.doc.views.resource_detail', name='resource-detail'),
                       )
