# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

class RssSource(models.Model):
    """a Rss feed to use as source of items (which are used to create CMS articles)"""
    
    url = models.URLField(_('url'), unique=True)
    title = models.CharField(_(u"title"), max_length=200, blank=True, default="")
    last_collect = models.DateTimeField(_(u"last collect"), blank=True, null=True)
    
    def get_absolute_url(self):
        return self.url
    
    def __unicode__(self):
        return self.url

    class Meta:
        verbose_name = _(u'RSS source')
        verbose_name_plural = _(u'RSS sources')


class RssItem(models.Model):
    """a Rss item that can be used to create a CMS article"""
    
    source = models.ForeignKey(RssSource)
    link = models.URLField(_('link'))
    title = models.CharField(_(u"title"), max_length=200, blank=True)
    summary = models.TextField(_(u"summary"), blank=True)
    author = models.CharField(_(u"author"), max_length=200, blank=True)
    updated = models.DateTimeField(_(u"updated"), blank=True, null=True)
    processed = models.BooleanField(_(u"processed"), default=False)
    
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _(u'RSS item')
        verbose_name_plural = _(u'RSS items')
