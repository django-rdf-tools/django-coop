# -*- coding:utf-8 -*-

from django.conf.urls.defaults import *
#from django.views.generic import ListView
#from coop.org.views import ISDetailView
#from coop_local.models import Organization


urlpatterns = patterns('',

    # sympa test
    url(r'^sympa_remote_list/(?P<name>\w+)$', 'coop.mailing.views.list'),


)
