# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
import datetime
from coop_geo.models import Area, Location


EXCHANGE = Choices(
    ('OFFER',   0,  _(u'Offer')),
    ('NEED',    1,  _(u'Need')),
    ('SHARE',   2,  _(u'Sharing')),
    ('GIFT',    3,  _(u'Gift')),
    ('QA',      4,  _(u'Question')),
)


class BaseExchange(models.Model):
    title = models.CharField(_('title'),blank=True,max_length=250)
    description = models.TextField(_(u'description'),blank=True)
    org = models.ForeignKey('coop_local.Initiative',blank=True,null=True,verbose_name='publisher')
    member = models.ForeignKey('coop_local.Membre')
    etype = models.PositiveSmallIntegerField( _(u'classified type'),
                                                    choices=EXCHANGE.CHOICES, 
                                                    default=EXCHANGE.OFFER)
    expiration = models.DateField(default=datetime.datetime.today,blank=True,null=True)
    slug = exfields.AutoSlugField(populate_from='title')
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    
    uri = models.CharField(_(u'main URI'),blank=True, max_length=250, editable=False)
    author_uri = models.CharField(_(u'author URI'),blank=True, max_length=200)
    publisher_uri = models.CharField(_(u'publisher URI'),blank=True, max_length=200)
    
    location = models.ForeignKey(Location,null=True,blank=True,verbose_name=_(u'location'))
    area = models.ForeignKey(Area,null=True,blank=True,verbose_name=_(u'area'))
    
    
    class Meta:
        abstract = True
        

class BaseTransaction(models.Model):
    origin = models.ForeignKey('coop_local.Exchange',related_name='origin', verbose_name=_(u'origine'))
    destination = models.ForeignKey('coop_local.Exchange',related_name='destination', verbose_name=_(u'destination'))
    title = models.CharField(_('title'),blank=True,max_length=250)
    description = models.TextField(_(u'description'),blank=True)
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    uuid = exfields.UUIDField() #nécessaire pour URI ?
    
    class Meta:
        abstract = True