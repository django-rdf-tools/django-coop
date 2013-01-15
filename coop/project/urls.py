
# -*- coding:utf-8 -*-
from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url

# # https://code.djangoproject.com/ticket/10405#comment:11
# from django.db.models.loading import cache as model_cache
# if not model_cache.loaded:
#     model_cache.get_models()

urlpatterns = patterns('',
    url(r'^projets/$', 'coop.project.views.projects_list', name="projects_list"),
    url(r'^projet/(?P<id>[\d]+)/detail/$', 'coop.project.views.project_detail', name="project_detail"),
    url(r'^projets/map/$', 'coop.project.views.projects_map', name="projects_map"),
)


