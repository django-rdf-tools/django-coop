# -*- coding: utf-8 -*-
from django.contrib import admin
from rss_sync import models, views
from widgets import AdminCollectRssWidget
from django.utils.translation import ugettext_lazy as _
from rss_sync.forms import RssSourceAdminForm, RssItemAdminForm

class RssSourceAdmin(admin.ModelAdmin):
    form = RssSourceAdminForm
    list_display = ('url', 'title', 'last_collect')
    readonly_fields = ('title', 'last_collect')
    fieldsets = (
        (_(u'Actions'), {'fields': ('id',)}),
        (_(u'Feed'), {'fields': ('url',)}),
        (_(u'Information'), {'fields': ('title', 'last_collect')}),
    )
    actions = [views.collect_rss_items_action]

admin.site.register(models.RssSource, RssSourceAdmin)


class RssItemAdmin(admin.ModelAdmin):
    form = RssItemAdminForm
    list_display = ('link', 'source', 'title', 'updated', 'processed')
    list_filter = ('source', 'processed')
    readonly_fields = ('source', 'link', 'updated', 'processed')
    fieldsets = (
        (_(u'Actions'), {'fields': ('id',)}),
        (_(u'Source'), {'fields': ('source', 'link', 'updated')}),
        (_(u'Content'), {'fields': ('title', 'summary')}),
        (_(u'CMS'), {'fields': ('processed',)}),
    )
    actions = [views.create_cms_article_action]


admin.site.register(models.RssItem, RssItemAdmin)
