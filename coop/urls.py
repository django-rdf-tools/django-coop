# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.base import TemplateView, RedirectView


class TextPlainView(TemplateView):
  def render_to_response(self, context, **kwargs):
    return super(TextPlainView, self).render_to_response(
      context, content_type='text/plain', **kwargs)

urlpatterns = patterns('',

    url(r'^$', 'coop.views.home', name="home"),
    url(r'^initiative/$', 'coop_local.views.org_list', name="org_list"), #view coop surchargée --> voir plutot les CBV
    (r'^initiative/', include('coop.org.urls')),
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    #url(r'^taggit_autocomplete_modified/', include('taggit_autocomplete_modified.urls')),
    (r'^search/', include('haystack.urls')),    
    (r'^comments/', include('django.contrib.comments.urls')),
    
    # a revoir
    (r'^perso/$', 'coop.person.views.perso'),
    (r'^membre/', include('coop.person.urls')),
    
    url(r'^robots\.txt$', TextPlainView.as_view(template_name='robots.txt')),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/media/img/favicon.ico')),
    
)

