# -*- coding:utf-8 -*-
from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url

# # https://code.djangoproject.com/ticket/10405#comment:11
# from django.db.models.loading import cache as model_cache
# if not model_cache.loaded:
#     model_cache.get_models()

admin.autodiscover()


# Add you own URLs here
urlpatterns = []

# urlpatterns += patterns('',
#    url(r'^org/$', 'coop_local.views.org_list', name="org_list"), #view coop
# )


from coop.default_project_urls import *


#    url(r'^org/$', 'coop_local.views.org_list', name="org_list"), #view coop a surcharger --> voir plutot les CBV
