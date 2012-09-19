# -*- coding:utf-8 -*-

from django.conf import settings
from coop.link.models import BaseLinkProperty, BaseLink
from coop.article.models import CoopArticle, CoopNavTree
from coop.person.models import BasePerson, BasePersonCategory
from coop.mailing.models import BaseSubscription, BaseMailingList
from coop.exchange.models import BaseExchange, BaseProduct, BaseExchangeMethod
from coop.org.models import (   BaseOrganizationCategory, BaseOrganization,
                                BaseRelation, BaseEngagement, BaseRole,
                                BaseContact, BaseRoleCategory)


# ---- person


class LinkProperty(BaseLinkProperty):
        pass


class Link(BaseLink):
        pass


# ----- CMS

class Article(CoopArticle):
    pass


class NavTree(CoopNavTree):
    pass

if 'coop_tag' in settings.INSTALLED_APPS:
    from coop.tag.models import CoopTag, CoopTaggedItem

    # ----- Tag

    class Tag(CoopTag):
        pass

    class TaggedItem(CoopTaggedItem):
        pass


# ---- person


class PersonCategory(BasePersonCategory):
        pass


class Person(BasePerson):
        pass


# ----- org


class Contact(BaseContact):
        pass


class RoleCategory(BaseRoleCategory):
        pass


class Role(BaseRole):
        pass


class Relation(BaseRelation):
        pass


class Engagement(BaseEngagement):
        pass


class OrganizationCategory(BaseOrganizationCategory):
        pass


class Organization(BaseOrganization):
        pass


# ------ exchange


class Exchange(BaseExchange):
        pass


class ExchangeMethod(BaseExchangeMethod):
        pass


class Product(BaseProduct):
        pass


# ----- mailing


class MailingList(BaseMailingList):
        pass


class Subscription(BaseSubscription):
        pass


# ----- agenda

if 'coop.agenda' in settings.INSTALLED_APPS:
    from coop.agenda.models import BaseCalendar, BaseEvent, BaseEventCategory, \
            BaseOccurrence, BaseDated

    class Calendar(BaseCalendar):
            pass

    class Event(BaseEvent):
            pass

    class EventCategory(BaseEventCategory):
            pass

    class Occurrence(BaseOccurrence):
            pass

    class Dated(BaseDated):
            pass



