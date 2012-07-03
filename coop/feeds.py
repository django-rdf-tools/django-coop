# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django_push.publisher.feeds import Feed
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType
import datetime


class UpdateFeed(Feed):
    title = _(u"Updates for %s." % Site.objects.get_current().name)
    link = "/feed/" 
    description = _(u"All records updates listed on the %s website." % Site.objects.get_current().name)
    hub = "http://%s/hub/" % Site.objects.get_current()


    def items(self):
        # Call content type pour trouver les models ....
        # ajouter les champs created 
        # ping dans save de model uri
        return get_model(self._mType.app_label, self._model).objects.order_by('-modified')[:5]

    # to deal with overwriting ...
    def item_title(self, item):
        try:
            return item.label()
        except:
            return item.label

    def item_link(self, item):
        return item.uri

    def item_guid(self, item):
        return "%s_%s" % (item.uuid, item.modified)

    def item_pubdate(self, item):
        return datetime.datetime.now()

    def item_description(self, item):
        # return item.uri + 'sparql endpoint' + uriSparql
        return item.uri

    # def item_extra_kwargs
    def get_object(self, request, *args, **kwargs):
        self._model = kwargs['model']
        self._mType = ContentType.objects.get(model=self._model)
        self.title = _(u"Updates for %s on %s." % (self._model, Site.objects.get_current().name))
        self.link = "/feed/%s/" % self._model
        return None




