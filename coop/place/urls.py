# -*- coding:utf-8 -*-

from django.conf.urls.defaults import *
from coop_local.models import Site

urlpatterns = patterns('',
    url(r'^(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}).html$', 
        'coop.place.views.detail', 
        name="place_detail"),  
)