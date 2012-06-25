# -*- coding:utf-8 -*-
# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.base import TemplateView, RedirectView
from django.conf import settings
from coop.feeds import UpdateFeed
import coop.signals


class TextPlainView(TemplateView):
    def render_to_response(self, context, **kwargs):
        return super(TextPlainView, self).render_to_response(
              context, content_type='text/plain', **kwargs)

urlpatterns = patterns('',

    url(r'^$', 'coop.views.home', name="home"),

    (r'^org/', include('coop.org.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),

    # a revoir
    (r'^perso/$', 'coop.person.views.perso'),
    (r'^membre/', include('coop.person.urls')),

    url(r'^feed/(?P<model>[\w-]+)/$', UpdateFeed()),

    url(r'^robots\.txt$', TextPlainView.as_view(template_name='robots.txt')),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
    url(r'^d2r/(?P<mode>[\w-]+)/mapping.ttl$', 'coop.views.d2r_mapping'),

)

if 'coop.exchange' in settings.INSTALLED_APPS:

    urlpatterns = urlpatterns + patterns('',
        (r'^annonces/', include('coop.exchange.urls')),
    )


def SentryHandler500(request):
    from django.template import Context, loader
    from django.http import HttpResponseServerError

    t = loader.get_template('500.html')  # You need to create a 500.html template.
    return HttpResponseServerError(t.render(Context({
        'request': request,
    })))

