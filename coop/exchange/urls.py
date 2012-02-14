# -*- coding:utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
#url(r'^$', 'coop.initiative.views.list', name="initiative_list"),
    url(r'^(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$', 
        'coop.exchange.views.exchange_detail', 
        name="exchange_detail"),
)
