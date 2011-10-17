# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from rss_sync.models import RssSource, RssItem
from coop_cms.models import Article
import feedparser
from datetime import datetime
from time import mktime
from django.conf import settings

def collect_rss_items(user, source, check_user_rights=True):
    """
    download a rss feed and create rss_items
    the source can be a RssSource or any object with a get_absolute_url method
    """
    if check_user_rights and (not (user.is_staff and user.has_perm('rss_sync.add_rssitem'))):
        raise PermissionDenied

    f = feedparser.parse(source.get_absolute_url())
    
    for e in f.entries:
        #create RSS entries if not exists
        item, _is_new = RssItem.objects.get_or_create(link=e.link, source=source)
        #In any case, update the data
        item.title = e.title
        item.updated = datetime.fromtimestamp(mktime(e.updated_parsed))
        item.author = getattr(e, 'author', '')[:100]
        item.summary = e.summary
        item.save()
    
    if isinstance(source, RssSource):
        #update info for rss sources only
        source.title = getattr(f.feed, 'title', '')
        source.last_collect = datetime.now()
        source.save()


def collect_all_rss_items():
    all_models = getattr(settings, 'RSS_SYNC_SOURCE_MODELS', [RssSource])
    for model in all_models:
        for source in model.objects.all():
           collect_rss_items(None, source, check_user_rights=False)


def create_cms_article(user, item):
    """create a cms coop_cms.article from a RssItem"""
    if not (user.is_staff and user.has_perm('coop_cms.add_article')):
        raise PermissionDenied
    
    art = Article.objects.create(title=item.title, content=item.summary)
    item.processed = True
    item.save()
    return art

