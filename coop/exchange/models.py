# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
import datetime


EXCHANGE = Choices(
    ('OFFER',   0,  'Offre'),
    ('NEED',    1,  'Demande'),
)


class BaseExchange(models.Model):
    title = models.CharField(_('Titre'),blank=True,max_length=250)
    description = models.TextField(_(u'Description'),blank=True)
    org = models.ForeignKey('coop_local.Initiative',blank=True,null=True)
    member = models.ForeignKey('coop_local.Membre')
    etype = models.PositiveSmallIntegerField( _(u'Type d’annonce'),
                                                    choices=EXCHANGE.CHOICES, 
                                                    default=EXCHANGE.OFFER)
    uri = models.CharField(_(u'URI principale'),blank=True, max_length=250, editable=False)
    expiration = models.DateField(default=datetime.datetime.today,blank=True,null=True)
    slug = exfields.AutoSlugField(populate_from='title')
    created = exfields.CreationDateTimeField(_(u'Création'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'Modification'),null=True)
    #membre_uri = models.CharField(_(u'Profil FOAF'),blank=True, max_length=250, editable=False)
    class Meta:
        abstract = True
        

class BaseTransaction(models.Model):
    origin = models.ForeignKey('coop_local.Exchange',related_name='origin')
    destination = models.ForeignKey('coop_local.Exchange',related_name='destination')
    title = models.CharField(_('Titre'),blank=True,max_length=250)
    description = models.TextField(_(u'Description'),blank=True)
    created = exfields.CreationDateTimeField(_(u'Création'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'Modification'),null=True)
    uuid = exfields.UUIDField() #nécessaire pour URI de l'engagement
    class Meta:
        abstract = True