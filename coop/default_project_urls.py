# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
#from coop.webid import webiduri
import sys

# https://code.djangoproject.com/ticket/10405#comment:11
# from django.db.models.loading import cache as model_cache
# if not model_cache.loaded:
#     model_cache.get_models()

from coop_local.urls import urlpatterns

handler500 = 'coop.views.SentryHandler500'

urlpatterns += patterns('',

    #Testing webid urls
    # url(r'^accounts/webidauth', 'coop.webid.views.test_login',
    #     name="webidauth-login"),
    # url(r'^webid/', include('django_webid.provider.urls')),
    # url(r'^auth/', include('coop.webid.urls')),

    #XXX remove this first url. Just debuggin'
    # url(r'^testpeople/(?P<username>\S+)', 'coop.webid.views.people',
    #     name="webidprovider-webid_uri.test"),
    # This url is used for assigning the WebID URI for
    # a user if no callback is given in settings.
    # url(r'^people/(?P<username>\S+)$',
    #     webiduri.WebIDProfileView.as_view(),
    #     name="webidprovider-webid_uri"),

    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/password_reset/$', 'django.contrib.auth.views.password_reset', name='admin_password_reset'),
    url(r'^admin/password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
    #url(r'^org/$', 'coop_local.views.org_list', name="org_list"),  # exemple de view django-coop surchargee
)


# URLS for all Classification models

# from django.db.models.loading import get_models
# from coop.org.models import BaseClassification
# from django.views.generic.detail import DetailView

# for model in [x for x in get_models() if BaseClassification in x.__mro__]:
#     urlpatterns += patterns('',
#         url(r'^%s/(?P<slug>[-_\w|\W]+)/$' % model._meta.object_name.lower(),
#             DetailView.as_view(
#                 model=model,
#                 template_name='org/%s-detail.html' % model._meta.object_name.lower()
#             ), name='%s-detail' % model._meta.object_name.lower()),
#     )


# for local testing
if settings.DEBUG or ('test' in sys.argv) or ('runserver' in sys.argv):
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )


if 'coop_tag' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^', include('coop_tag.urls')),
    )

if 'coop.agenda' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^', include('coop.agenda.urls')),
    )

urlpatterns += patterns('',
    (r'^forms/', include('forms_builder.forms.urls')),
    (r'^id/', include('uriredirect.urls')),
    (r'^data/', include('coop.data_urls')),
    (r'^', include('coop_geo.urls', app_name='coop_geo')),
    (r'^djaloha/', include('djaloha.urls')),
    (r'^', include('coop.urls')),
    (r'^', include('coop_cms.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
    # url(r'^', include('debug_toolbar_htmltidy.urls'))
    # url(r'^', include('debug_toolbar_user_panel.urls')),
)
