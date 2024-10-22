# -*- coding:utf-8 -*-

from django.conf.urls.defaults import *
#from django.views.generic import ListView
#from coop.org.views import ISDetailView
#from coop_local.models import Organization


urlpatterns = patterns('coop.mailing.views',

    # sympa test
    url(r'^sympa_remote_list/(?P<name>[-\w]+)/$', 'sympa_remote_list', name='sympa_remote_list'),
    url(r'^newsletter/new/$', 'new_newsletter', name='new_newsletter'),
    url(r'^newsletter/settings/(?P<newsletter_id>\d+)/$', 'new_newsletter', name='newsletter_settings'),
    url(r'^newsletter/(?P<newsletter_id>\d+)/$', 'view_newsletter', name='coop_view_newsletter'),
    url(r'^newsletter/(?P<newsletter_id>\d+)/cms_edit/$', 'edit_newsletter', name='coop_edit_newsletter'),
    url(r'^newsletter/change-template/(?P<newsletter_id>\d+)/$', 'change_newsletter_template', name="change_newsletter_template"),
    url(r'^newsletter/test/(?P<newsletter_id>\d+)/$', 'test_newsletter', name="test_newsletter"),
    url(r'^newsletter/schedule/(?P<newsletter_id>\d+)/$', 'schedule_newsletter_sending', name="schedule_newsletter_sending"),
    url(r'^newsletter/abonnement/(?P<uuid>\w+)/$', 'modif_abonnement', name="modif_abonnement"),
    url(r'^mailing/delsub/', 'delete_subscription', name='delete_subscription'),
    url(r'^mailing/delnewselement/', 'delete_newselement', name='delete_newselement'),

)
