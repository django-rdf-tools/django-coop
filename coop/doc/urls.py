
# -*- coding:utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('', url(r'^resource/(?P<slug>[\w-]+)/$',
                       'coop.doc.views.resource_detail',
                       name='resource-detail'),
                       )
