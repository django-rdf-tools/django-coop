# -*- coding:utf-8 -*-

from django.conf.urls.defaults import *
#from django.views.generic import ListView
#from coop.org.views import ISDetailView
#from coop_local.models import Organization


urlpatterns = patterns('',

    url(r'^$', 'coop.org.views.org_list', name="org_list"),
    url(r'^carto/$', 'coop.org.views.leaflet', name="leaflet"),

    url(r'^categorie/(?P<slug>[\w-]+)/$', 'coop.org.views.org_category_detail', name="org_category_detail"),

    url(r'^global_map$', 'coop.org.views.global_map', name="org_global_map"),
    url(r'^(?P<slug>[\w-]+)/$', 'coop.org.views.org_detail_view', name="org_detail"),
    url(r'^(?P<slug>[\w-]+)/edit/$', 'coop.org.views.org_edit', name="org_edit"),

    #url(r'^role/(?P<slug>[\w-]+)/$', 'coop.org.views.role_detail', name="role_detail"),


)
