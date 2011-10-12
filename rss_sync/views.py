# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rss_sync.models import RssSource, RssItem
from django.core.exceptions import PermissionDenied
import feedparser
from datetime import datetime
from time import mktime
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from coop_cms.models import Article

def collect_rss_items(source):
    """
    download a rss feed and create rss_items
    the source can be a RssSource or any object with a get_absolute_url method
    """
    f = feedparser.parse(source.get_absolute_url())
    
    for e in f.entries:
        #create RSS entries if not exists
        item, _is_new = RssItem.objects.get_or_create(link=e.link, source=source)
        #In any case, update the data
        item.title = e.title
        item.updated = datetime.fromtimestamp(mktime(e.updated_parsed))
        item.author = e.author[:100]
        item.summary = e.summary
        item.save()
    
    if isinstance(source, RssSource):
        #update info for rss sources only
        source.title = f.feed.title
        source.last_collect = datetime.now()
        source.save()

def collect_rss_items_view(request, source_id):
    """The view called when clicking on the button in the object admin form"""
    rss_source = get_object_or_404(RssSource, id=source_id)
    
    if not (request.user.is_staff and request.user.has_perm('rss_sync.add_rssitem')):
        raise PermissionDenied
    
    collect_rss_items(rss_source)
    
    url = reverse('admin:rss_sync_rssitem_changelist')+u'?source__id__exact={0}'.format(rss_source.id)
    return HttpResponseRedirect(url)

def collect_rss_items_action(modeladmin, request, queryset):
    """The action called when executed from admin list of rss sources"""
    for source in queryset:
        collect_rss_items(source)
    url = reverse('admin:rss_sync_rssitem_changelist')
    return HttpResponseRedirect(url)
collect_rss_items_action.short_description = _(u'Collect RSS items')

def create_cms_article(item):
    """create a cms coop_cms.article from a RssItem"""
    art = Article.objects.create(title=item.title, content=item.summary)
    item.processed = True
    item.save()
    return art
    
def create_cms_article_view(request, item_id):
    """The view called when clicking on the button in admin object form"""
    item = get_object_or_404(RssItem, id=item_id)
    art = create_cms_article(item)
    return HttpResponseRedirect(art.get_edit_url()) #redirect to cms article edit page
    
def create_cms_article_action(modeladmin, request, queryset):
    """The action called when executed from admin list of rss items"""
    for item in queryset:
        art = create_cms_article(item)
    if queryset.count()==1: #if only 1 item processed (checked)
        return HttpResponseRedirect(art.get_edit_url()) #redirect to cms article edit page
create_cms_article_action.short_description = _(u'Create CMS Article')