# -*- coding:utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic import ListView
from coop.initiative.views import ISDetailView
from coop_local.models import Initiative

urlpatterns = patterns('',
    (r'^$', ListView.as_view(
        model=Initiative,
        context_object_name='liste_initiatives',
        template_name='initiative/initiative_list.html'
        )),
    
    url(r'^(?P<slug>\w+).html$', 'coop.initiative.views.ISDetailView', name="initiative_detail"),
    #     
    # (r'^(?P<slug>\w+).html$', ISDetailView.as_view(
    #     model=Initiative,
    #     #context_object_name='liste_initiatives'
    #     template_name = 'initiative_detail.html'
    #     
    #     )),    
        
)