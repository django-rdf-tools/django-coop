# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __
from django.core.exceptions import ValidationError
from django_extensions.db.fields import AutoSlugField

class Page(models.Model):
    slug = AutoSlugField(populate_from='title', max_length=100, unique=True)
    title = models.TextField(_(u'title'), default=_('Page title'))
    content = models.TextField(_(u'content'), default=_('Page content'))
    
    class Meta:
        verbose_name = _(u"page")
        verbose_name_plural = _(u"pages")
    
    def __unicode__(self):
        return self.slug
    
    def get_label(self):
        return self.title
    
    def get_absolute_url(self):
        return u'/'+self.slug
    