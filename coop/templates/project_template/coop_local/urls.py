# -*- coding:utf-8 -*-
from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# # https://code.djangoproject.com/ticket/10405#comment:11
# from django.db.models.loading import cache as model_cache
# if not model_cache.loaded:
#     model_cache.get_models()

admin.autodiscover()


# Add you own URLs here
urlpatterns = []

# urlpatterns += patterns('',
#    url(r'^$', 'coop_local.views.home', name="home"),
#    url(r'^org/$', 'coop_local.views.org_list', name="org_list"), #view coop

# )


from coop.default_project_urls import urlpatterns as default_project_urls
urlpatterns += default_project_urls


