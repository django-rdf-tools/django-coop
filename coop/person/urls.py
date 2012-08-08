# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url

from django.contrib.auth import views as auth_views
from forms import ProfileForm

urlpatterns = patterns('',

    (r'^login/$', 'django.contrib.auth.views.login', {'template_name':'accounts/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name':'accounts/logout.html'}),
    
    # interception de la page edition de profil pour injecter notre formulaire
    (r'^edit/$', 'profiles.views.edit_profile', {'form_class': ProfileForm,}),
    
    # url(r'^(?P<username>[_a-z]+)/$', 'profiles.views.profile_detail', name='profiles_profile_detail'),

    url(r'^password/change/$',auth_views.password_change,name='auth_password_change'),
    url(r'^password/change/done/$',auth_views.password_change_done,name='auth_password_change_done'),
    url(r'^password/reset/$',auth_views.password_reset,name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',auth_views.password_reset_confirm,name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',auth_views.password_reset_complete,name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',auth_views.password_reset_done,name='auth_password_reset_done'),
    
    # sinon on délégue à l'app profiles
    (r'^', include('profiles.urls')),
    
  
)
