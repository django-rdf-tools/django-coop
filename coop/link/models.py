# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django_extensions.db import fields as exfields

class BaseSemLink(models.Model):
    """Linked Data generic link model, can apply to SeeAlso or SameAs"""
    url             = models.URLField(blank=True, verify_exists=True, verbose_name=_(u'URL'))
    label           = models.CharField(_(u'Label'),max_length=100)
    slug            = exfields.AutoSlugField(populate_from=('label'))
    created         = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified        = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    content_type    = models.ForeignKey(ContentType, blank=True, null=True)
    object_id       = models.PositiveIntegerField()
    content_object  = generic.GenericForeignKey('content_type', 'object_id')
    
    # TODO et author uri etc ?
    
    def __unicode__(self):
        return self.label
    class Meta :
        abstract = True
        
        

