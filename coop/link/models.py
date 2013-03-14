# # -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django_extensions.db import fields as exfields
from django.core.exceptions import ImproperlyConfigured
from django.db.models.base import ObjectDoesNotExist
#from django.core.exceptions import ObjectDoesNotExist
from django.db.models.loading import get_model

class BaseLinkProperty(models.Model):
    label = models.CharField(_(u'Label'), max_length=100)
    uri = models.URLField(blank=True, verbose_name=_(u'property URI'))  # verify_exists=False,

    class Meta:
        abstract = True
        verbose_name = _(u'linking property')
        verbose_name_plural = _(u'linking properties')
        app_label = 'coop_local'

    def __unicode__(self):
        return self.label


class BaseLink(models.Model):
    """
    generic link model, recording some properties about an object URI
    SeeAlso or SameAs
    """
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    predicate = models.ForeignKey('coop_local.LinkProperty')
    object_uri = models.URLField(blank=True, verbose_name=_(u'object URI'), default='http://')  # verify_exists=False, 
    object_label = models.CharField(_(u'link label'), max_length=150, blank=True, null=True)

    def __unicode__(self):
        return u"%s %s %s" % (unicode(self.content_object), unicode(self.predicate), self.object_uri)

    class Meta:
        abstract = True
        verbose_name = _(u'semantic link')
        verbose_name_plural = _(u'semantic links')
        app_label = 'coop_local'

    def save(self, *args, **kwargs):
        #import pdb; pdb.set_trace()
        if not self.predicate_id:
            try:
                see_also = get_model('coop_local','LinkProperty').objects.get(label='seeAlso')
                self.predicate = see_also
            except ObjectDoesNotExist:
                raise ImproperlyConfigured("No seeAlso RDF property available. Please check that LinkProperty fixtures have been loaded during django-coop setup. ")
        super(BaseLink, self).save(*args, **kwargs)

