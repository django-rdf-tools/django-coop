# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _


class BaseRole(models.Model):
    label = models.CharField(_(u'Intitulé'),max_length=30)
    slug = exfields.AutoSlugField(populate_from=('label'))
    class Meta:
        abstract = True
    def __unicode__(self):
        return unicode(self.label) 

class BaseEngagement(models.Model):
    membre = models.ForeignKey('coop_local.Membre',related_name='pkid')
    initiative = models.ForeignKey('coop_local.Initiative')
    role = models.ForeignKey('coop_local.Role')
    created = exfields.CreationDateTimeField(_(u'Création rôle'))
    modified = exfields.ModificationDateTimeField(_(u'Modification rôle'))
    #membre_uri = models.CharField(_(u'Profil FOAF'),blank=True, max_length=250, editable=False)
    uuid = exfields.UUIDField() #nécessaire pour URI de l'engagement
    class Meta:
        abstract = True
        
    '''
    def save(self):
        ramener URI du membre / mais D2R peut bien linker le champ de membre ?
    '''    

class BaseInitiative(models.Model):
    title = models.CharField(_('Titre'),max_length=250)
    description = models.TextField(_(u'Description'))
    uri = models.CharField(_(u'URI principale'),blank=True, max_length=250, editable=False)
    telephone_fixe = models.CharField(_(u'Téléphone fixe'),blank=True, max_length=14)
    email = models.EmailField(_(u'Email général'),blank=True)
    web = models.URLField(_(u'Site web'),blank=True, verify_exists=True)
    rss = models.URLField(_(u'Flux RSS'),blank=True, verify_exists=True)
    slug = exfields.AutoSlugField(populate_from='title')
    created = exfields.CreationDateTimeField(_(u'Création fiche'))
    modified = exfields.ModificationDateTimeField(_(u'Modification fiche'))
    class Meta:
        abstract = True
    def __unicode__(self):
        return unicode(self.title)
        
    #@models.permalink
    def get_absolute_url(self):
        return ('/is/'+self.slug+'.html')
    
    def local_uri(self):
        return ('http://dev.credis.org:8000/is/'+self.slug+'/')





   
    
    