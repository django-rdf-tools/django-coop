#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import permission_required

from views import JSONLocationView

urlpatterns = patterns('',
    url(r'^location/json/(?P<city>\w+)/(?P<address>\w.*)?$',
     permission_required('coop_geo.add_location')(JSONLocationView.as_view()),
     name='json_location'),
)
