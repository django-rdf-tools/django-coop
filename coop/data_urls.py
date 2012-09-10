# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    (r'^(?P<model>[a-z]+)/(?P<uuid>\w+).(?P<format>\w+)$', 'coop.views.get_rdf'),  # [xml,n3,ttl,json, trix]
)

