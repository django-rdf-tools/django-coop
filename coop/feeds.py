# -*- coding:utf-8 -*-

from django.utils.translation import ugettext_lazy as _
#from django.contrib.syndication.views import Feed
from coop_local.models import Organization
from django.contrib.sites.models import Site
from django_push.publisher.feeds import Feed

from django.conf import settings

# sparql endPoint....served by jetty in localhost
# This config is yet a little bit hard coded.... To be generalized in the futur



uriSparql = 'http://localhost:8080/' + settings.PROJECT_NAME + '/sparql'




class OrganizationUpdates(Feed):
    title = _(u"Organization updates for %s." % Site.objects.get_current().name)
    link = "/organizations/"
    description = _(u"All records updates for organizations listed on the %s website." % Site.objects.get_current().name)

    # description_template = "feeds/rdf_payload.html"

    # Only local organization can be in the feed. Imported organization are
    # updated by their owners site.
    def items(self):
        return Organization.objects.order_by('-modified')[:5]

    def item_title(self, item):
        return item.label()

    # def item_extra_kwargs


    def item_description(self, item):
        # return item.description
        return item.toJson()
        # return item.uri + 'sparql endpoint' + uriSparql





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


