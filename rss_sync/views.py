# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rss_sync.models import RssSource, RssItem
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from rss_sync.utils import collect_rss_items, create_cms_article

def collect_rss_items_view(request, source_id):
    """The view called when clicking on the button in the object admin form"""
    rss_source = get_object_or_404(RssSource, id=source_id)
    
    collect_rss_items(request.user, rss_source)
    
    url = reverse('admin:rss_sync_rssitem_changelist')+u'?source__id__exact={0}'.format(rss_source.id)
    return HttpResponseRedirect(url)

def collect_rss_items_action(modeladmin, request, queryset):
    """The action called when executed from admin list of rss sources"""
    for source in queryset:
        collect_rss_items(request.user, source)
    url = reverse('admin:rss_sync_rssitem_changelist')
    return HttpResponseRedirect(url)
collect_rss_items_action.short_description = _(u'Collect RSS items')

    
def create_cms_article_view(request, item_id):
    """The view called when clicking on the button in admin object form"""
    item = get_object_or_404(RssItem, id=item_id)
    art = create_cms_article(request.user, item)
    return HttpResponseRedirect(art.get_edit_url()) #redirect to cms article edit page
    
def create_cms_article_action(modeladmin, request, queryset):
    """The action called when executed from admin list of rss items"""
    for item in queryset:
        art = create_cms_article(request.user, item)
    if queryset.count()==1: #if only 1 item processed (checked)
        return HttpResponseRedirect(art.get_edit_url()) #redirect to cms article edit page
create_cms_article_action.short_description = _(u'Create CMS Article')