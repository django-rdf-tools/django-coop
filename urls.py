# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',

    url("^$", direct_to_template, {"template": "base.html"}, name="home"),
#url(r"^$", 'views.home', name="home"),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    (r'^membre/', include('membre.urls')),
  
)

urlpatterns += staticfiles_urlpatterns()
