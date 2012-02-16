# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.generic.base import TemplateView, RedirectView
import sys

import oembed
oembed.autodiscover()

# https://code.djangoproject.com/ticket/10405#comment:11
from django.db.models.loading import cache as model_cache
if not model_cache.loaded:
    model_cache.get_models()
    
admin.autodiscover()

class TextPlainView(TemplateView):
  def render_to_response(self, context, **kwargs):
    return super(TextPlainView, self).render_to_response(
      context, content_type='text/plain', **kwargs)

urlpatterns = patterns('',

    url(r'^admin_tools/', include('admin_tools.urls')),
    
    url(r'^robots\.txt$', TextPlainView.as_view(template_name='robots.txt')),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/media/img/favicon.ico')),
    
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    #url(r'^taggit_autocomplete_modified/', include('taggit_autocomplete_modified.urls')),
    (r'^search/', include('haystack.urls')),
    
    url(r'^$', 'coop.views.home', name="home"),

    (r'^comments/', include('django.contrib.comments.urls')),

    #(r'^chaining/', include('smart_selects.urls')),
    
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^settings/', include('livesettings.urls')),
    (r'^perso/$', 'coop.person.views.perso'),
    (r'^initiative/', include('coop.initiative.urls')),
    url(r'^tag/(?P<slug>[\w-]+)/$', 'coop_tag.views.tag_detail', name="tag_detail"),
    
    (r'^rss-sync/', include('rss_sync.urls')),
    (r'^membre/', include('coop.person.urls')),
    (r'^djaloha/', include('djaloha.urls')),
    
    
)

if settings.DEBUG or ('test' in sys.argv):
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    )

urlpatterns += patterns('',
    (r'^', include('coop_geo.urls', app_name='coop_geo')),
    (r'^', include('coop_cms.urls')),
    #(r'^', include('uriresolve.urls')),
    
)
