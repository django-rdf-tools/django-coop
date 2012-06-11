# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django_push.publisher.feeds import Feed
#from django.contrib.syndication.views import Feed
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType



class UpdateFeed(Feed):
    title = _(u"Updates for %s." % Site.objects.get_current().name)
    link = "%s/feed/" % Site.objects.get_current().domain
    description = _(u"All records updates listed on the %s website." % Site.objects.get_current().name)


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


    def item_description(self, item):
        # return item.uri + 'sparql endpoint' + uriSparql
        return item.toJson()

    # def item_extra_kwargs
    def get_object(self, request, *args, **kwargs):
        self._model = kwargs['model']
        self._mType = ContentType.objects.get(model=self._model)
        return None



# import datetime
# import PyRSS2Gen
# orgs = Organization.objects.order_by('-modified')[:5]

# rss = PyRSS2Gen.RSS2(
#     title = u'Organization updates for APEAS.',
#     link = u'http://localhost:8000/organizations/',
#     description = "Dalke Scientific today announced PyRSS2Gen-0.0, "
#                        "a library for generating RSS feeds for Python.  ",
#     language = u'fr-FR',

#     lastBuildDate = datetime.datetime.utcnow(),

#     items = [
#        PyRSS2Gen.RSSItem(
#          title = orgs[0].title,
#          link = orgs[0].get_absolute_url(),
#          description = '<![CDATA[' + orgs[0].toXml() + ']]',
#          guid = PyRSS2Gen.Guid("http://www.dalkescientific.com/writings/"
#                                "diary/archive/2003/09/06/RSS.html"),

#          pubDate = datetime.datetime(2003, 9, 6, 21, 31)),
#        PyRSS2Gen.RSSItem(
#          title = orgs[1].title,
#          link = orgs[1].get_absolute_url(),
#          description = '<![CDATA[' + orgs[1].toXml() + ']]',
#          guid = PyRSS2Gen.Guid("http://www.dalkescientific.com/news/"
#                           "030906-PyRSS2Gen.html"),

#          pubDate = datetime.datetime(2003, 9, 6, 21, 31)),
#     ])


# rss.to_xml()
# rss.write_xml(open("pyrss2gen.xml", "w"))


