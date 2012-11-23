# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, redirect
from coop_local.models import Organization
from django.template import RequestContext
from django.conf import settings

# def org_list(request):
#     context = {}
#     context['org_list'] = Organization.objects.filter(active=True).order_by('statut')
#     return render_to_response('org/org_list.html',context,RequestContext(request))


if 'haystack' in settings.INSTALLED_APPS:
    from haystack.views import SearchView
    from coop_local.models import Article, Exchange, Event

    class ModelSearchView(SearchView):
        def __name__(self):
            return "FacetedSearchView"

        def extra_context(self):
            extra = super(ModelSearchView, self).extra_context()

            if self.results == []:
                extra['org'] = self.form.search().models(Organization)
                extra['exchange'] = self.form.search().models(Exchange)
                extra['article'] = self.form.search().models(Article)
                extra['event'] = self.form.search().models(Event)
            else:
                extra['org'] = self.results.models(Organization)
                extra['exchange'] = self.results.models(Exchange)
                extra['article'] = self.results.models(Article)
                extra['event'] = self.results.models(Event)

            return extra
