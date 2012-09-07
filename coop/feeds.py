# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django_push.publisher.feeds import Feed
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType
from coop.signals import LastDTProcess


class UpdateFeed(Feed):
    title = _(u"Updates for %s." % Site.objects.get_current().name)
    link = "/feed/"
    description = _(u"All records updates listed on the %s website." % Site.objects.get_current().name)
    hub = "http://%s/hub/" % Site.objects.get_current()

    description_template = 'feeds/description.html'  
    title_template = 'feeds/title.html'


    def items(self):
        # Call content type pour trouver les models ....
        # TODO : object such as uri_mode = 'common' or 'imported' are also published.
        # Is it the good feature?
        # return get_model(self._mType.app_label, self._model).objects.order_by('-modified')[:5]
        # print 'FeedItem CALLLED'
        qs = get_model(self._mType.app_label, self._model).objects.filter(modified__gte=LastDTProcess.get())
        if len(qs) > 5:
            return qs.order_by('-modified')
        else:
            return get_model(self._mType.app_label, self._model).objects.order_by('-modified')[:5]


    def item_link(self, item):
        return item.uri

    def item_guid(self, item):
        return "%s_%s" % (item.uuid, item.modified)

    def item_pubdate(self, item):
        return item.modified

    def item_categories(self, item):
        return ('django', 'coop')


    # def item_extra_kwargs
    def get_object(self, request, *args, **kwargs):
        self._model = kwargs['model']
        try:
            self._mType = ContentType.objects.get(model=self._model)
        except ContentType.MultipleObjectsReturned:
            self._mType = ContentType.objects.get(model=self._model, app_label='coop_local')


        self.title = _(u"Updates for %s on %s." % (self._model, Site.objects.get_current().name))
        self.link = "/feed/%s/" % self._model
        return None



