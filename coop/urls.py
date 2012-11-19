# -*- coding:utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.views.generic.base import TemplateView, RedirectView
from django.conf import settings
from coop.feeds import UpdateFeed


class TextPlainView(TemplateView):
    def render_to_response(self, context, **kwargs):
        return super(TextPlainView, self).render_to_response(
              context, content_type='text/plain', **kwargs)

urlpatterns = patterns('',

    url(r'^$', 'coop.views.home', name="home"),

    url(r'^org/', include('coop.org.urls')),
    url(r'^geojson/(?P<what>[\w-]+)/(?P<criteria>[\w-]+)/$', 'coop.views.geojson_objects'),

    url(r'^comments/', include('django.contrib.comments.urls')),

    # a revoir
    (r'^profil/', include('coop.person.urls')),

    url(r'^feed/(?P<model>[\w-]+)/$', UpdateFeed()),
    url(r'^hub/', include('subhub.urls')),
    url(r'^subscriber/', include('django_push.subscriber.urls')),  # Callback

    url(r'^robots\.txt$', TextPlainView.as_view(template_name='robots.txt')),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
    url(r'^rdfdump/(?P<model>[\w-]+).(?P<format>[\w-]+)$', 'coop.views.rdfdump'),

    # url(r'^d2r/(?P<mode>[\w-]+)/mapping.ttl$', 'coop.views.d2r_mapping'),

    url(r'^communes/$', 'coop.views.communes'),
    url(r'^geojson/', 'coop.views.geojson'),

)

if 'coop.exchange' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + patterns('',
        (r'^annonces/', include('coop.exchange.urls')),
)

if 'coop.webid' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + patterns('',
        (r'^webid/', include('coop.webid.urls')),
)
