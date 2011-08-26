# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

# class SameAs(models.Model):
#     uri = models.URLField(verify_exists=False,unique=True)

class BaseMembre(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, unique=True,verbose_name=_(u'Utilisateur'))
    #uri = models.URLField(blank=True, unique=True, verify_exists=False,verbose_name=_(u'URI principale'))
    #sameas = models.ManyToManyField(SameAs,blank=True, null=True,verbose_name=_(u'Autres URI'))
    nom = models.CharField(_(u'Nom'),max_length=100)
    prenom = models.CharField(_(u'Prénom'),max_length=100)
    adresse = models.TextField(_(u'Adresse'),blank=True)
    ville = models.CharField(_(u'Ville'),blank=True, max_length=100)
    code_postal = models.CharField(_(u'Code postal'),blank=True, max_length=5)
    telephone_fixe = models.CharField(_(u'Téléphone fixe'),blank=True, max_length=14)
    telephone_portable = models.CharField(_(u'Téléphone mobile'),blank=True, max_length=14)
    email = models.EmailField(_(u'Email personnel'),blank=True)
    class Meta:
        abstract = True
    def __unicode__(self):
        return self.prenom+u' '+self.nom
    @models.permalink
    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })
        
    def liste_engagements(self):
        return '' 
        
    '''
    def save(self):
        if(self.uri == None):
            set_uri
            linked_notification(self, creation)
        else:
            if(not uri.is_local()):
                linked_notification(self, haschanged ?)
            
            
    '''