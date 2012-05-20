# -*- coding:utf-8 -*-

from django.utils.translation import ugettext_lazy as _
#from django.contrib.syndication.views import Feed
from coop_local.models import Organization
from django.contrib.sites.models import Site
from django_push.publisher.feeds import Feed


class OrganizationUpdates(Feed):
    title = _(u"Organization updates for %s." % Site.objects.get_current().name)
    link = "/organizations/"
    description = _(u"All records updates for organizations listed on the %s website." % Site.objects.get_current().name)

    def items(self):
        return Organization.objects.order_by('-modified')[:5]

    def item_title(self, item):
        return item.label()

    def item_description(self, item):
        return item.description

