# -*- coding:utf-8 -*-

from django.conf.urls.defaults import *
#from django.views.generic import ListView
#from coop.org.views import ISDetailView
#from coop_local.models import Organization


urlpatterns = patterns('',

    url(r'^$', 'coop.org.views.org_list', name="org_list"),
    url(r'^cartographie/$', 'coop.org.views.leaflet', name="org_global_map"),
    #url(r'^global_map$', 'coop.org.views.global_map', name="org_global_map"),

    url(r'^categorie/(?P<slug>[\w-]+)/$', 'coop.org.views.org_category_detail', name="org_category_detail"),
    url(r'^categorie/(?P<slug>[\w-]+)/edition/$', 'coop.org.views.org_category_edit', name="org_category_edit"),
    url(r'^categorie/(?P<slug>[\w-]+)/edition/annuler/$', 'coop.org.views.org_category_edit_cancel', name="org_category_edit_cancel"),



    url(r'^(?P<slug>[\w-]+)/$', 'coop.org.views.org_detail', name="org_detail"),
    url(r'^(?P<slug>[\w-]+)/edition/$', 'coop.org.views.org_edit', name="org_edit"),
    url(r'^(?P<slug>[\w-]+)/edition/annuler/$', 'coop.org.views.org_edit_cancel', name='org_edit_cancel'),

    #url(r'^role/(?P<slug>[\w-]+)/$', 'coop.org.views.role_detail', name="role_detail"),


)
