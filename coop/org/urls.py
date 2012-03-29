# -*- coding:utf-8 -*-

from django.conf.urls.defaults import *
#from django.views.generic import ListView
#from coop.org.views import ISDetailView
#from coop_local.models import Organization

urlpatterns = patterns('',

    # (r'^$', ListView.as_view(
    #     model=Organization,
    #     context_object_name='liste_initiatives',
    #     template_name='initiative/initiative_list.html'
    #     )),

    url(r'^$', 'coop.org.views.org_list', name="org_list"),
    url(r'^global_map$', 'coop.org.views.global_map', name="org_global_map"),
    url(r'^(?P<slug>[\w-]+)/$', 'coop.org.views.org_detail_view', name="org_detail"),
    url(r'^(?P<slug>[\w-]+)/edit/$', 'coop.org.views.org_edit', name="org_edit"),
    
    url(r'^role/(?P<slug>[\w-]+)/$', 'coop.org.views.role_detail', name="role_detail"),
    
    #     
    # (r'^(?P<slug>\w+).html$', ISDetailView.as_view(
    #     model=Organization,
    #     #context_object_name='liste_initiatives'
    #     template_name = 'initiative_detail.html'
    #     
    #     )),    
        
)
