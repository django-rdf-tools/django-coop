from django.conf.urls.defaults import *
import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #XXX nameit, we can use it for the WEBIDAUTH_LOGIN_URL
    #(and that, in turn, for the decorator)
    url(r'^test/login$', views.test_login),
    url('^test/WebIDTest', views.webidlogin_report),
)
