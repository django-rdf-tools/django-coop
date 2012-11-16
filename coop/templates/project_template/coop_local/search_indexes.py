# -*- coding:utf-8 -*-
from haystack import indexes
from coop.search_indexes import OrganizationIndex as BaseOrganizationIndex
from coop.search_indexes import ExchangeIndex as BaseExchangeIndex
from coop.search_indexes import ArticleIndex as BaseArticleIndex
from coop.search_indexes import EventIndex as BaseEventIndex



# If you dont want to use the default index, please comment the following
# lines and write your own indexes



class OrganizationIndex(BaseOrganizationIndex, indexes.Indexable):
    pass


class ExchangeIndex(BaseExchangeIndex, indexes.Indexable):
    pass


class ArticleIndex(BaseArticleIndex, indexes.Indexable):
    pass


class EventIndex(BaseEventIndex, indexes.Indexable):
    pass
