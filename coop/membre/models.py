# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _

# class SameAs(models.Model):
#     uri = models.URLField(verify_exists=False,unique=True)

class BaseMembre(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, unique=True,verbose_name=_(u'Utilisateur'))
    #uri = models.URLField(blank=True, unique=True, verify_exists=False,verbose_name=_(u'URI principale'))
    #sameas = models.ManyToManyField(SameAs,blank=True, null=True,verbose_name=_(u'Autres URI'))
    nom = models.CharField(_(u'Nom'),max_length=100)
    prenom = models.CharField(_(u'Prénom'),max_length=100,null=True,blank=True)
    adresse = models.TextField(_(u'Adresse'),null=True,blank=True)
    ville = models.CharField(_(u'Ville'),null=True,blank=True, max_length=100)
    code_postal = models.CharField(_(u'Code postal'),null=True,blank=True, max_length=5)
    telephone_fixe = models.CharField(_(u'Téléphone fixe'),null=True,blank=True, max_length=14)
    telephone_portable = models.CharField(_(u'Téléphone mobile'),null=True,blank=True, max_length=14)
    email = models.EmailField(_(u'Email personnel'),blank=True)
    created = exfields.CreationDateTimeField(_(u'Création'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'Modification'),null=True)
    class Meta:
        abstract = True
    def __unicode__(self):
        return self.prenom+u' '+self.nom
    @models.permalink
    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })
        
    def engagements(self):
        eng = []
        for e in self.engagement_set.all():
            eng.append({'initiative':e.initiative,'role':e.role})
        return eng
        
    '''
    def save(self):
        if(self.uri == None):
            set_uri
            linked_notification(self, creation)
        else:
            if(not uri.is_local()):
                linked_notification(self, haschanged ?)
            
            
    '''