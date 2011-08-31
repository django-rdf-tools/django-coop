# -*- coding:utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic import ListView
from initiative.views import ISDetailView
from coop_local.models import Initiative

urlpatterns = patterns('',
    (r'^$', ListView.as_view(
        model=Initiative,
        context_object_name='liste_initiatives'
        )),
    (r'^(?P<slug>\w+).html$', ISDetailView.as_view(
        model=Initiative,
        context_object_name='liste_initiatives'
        )),    
)