# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
import datetime

class BaseCalendar(models.Model):
    title = models.CharField(_('Titre'),blank=True,max_length=250)
    description = models.TextField(_(u'Description'),blank=True)
    uri = models.CharField(_(u'URI principale'),blank=True, max_length=250, editable=False)
    slug = exfields.AutoSlugField(populate_from='title')
    created = exfields.CreationDateTimeField(_(u'Création'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'Modification'),null=True)
    #membre_uri = models.CharField(_(u'Profil FOAF'),blank=True, max_length=250, editable=False)
    class Meta:
        abstract = True
        

class BaseEvent(models.Model):
    calendar = models.ForeignKey('coop_local.Event')
    org = models.ForeignKey('coop_local.Initiative',blank=True,null=True)
    member = models.ForeignKey('coop_local.Membre')
    title = models.CharField(_('Titre'),blank=True,max_length=250)
    description = models.TextField(_(u'Description'),blank=True)
    datetime = models.DateField(default=datetime.datetime.today)
    slug = exfields.AutoSlugField(populate_from='title')
    created = exfields.CreationDateTimeField(_(u'Création'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'Modification'),null=True)
    #membre_uri = models.CharField(_(u'Profil FOAF'),blank=True, max_length=250, editable=False)
    uuid = exfields.UUIDField() #nécessaire pour URI de l'engagement
    class Meta:
        abstract = True        