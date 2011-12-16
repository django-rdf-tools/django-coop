# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from coop_geo.models import Location

class BaseMembre(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, unique=True,verbose_name=_(u'django user'))

    nom = models.CharField(_(u'first name'),max_length=100)
    prenom = models.CharField(_(u'last name'),max_length=100,null=True,blank=True)
    
    location = models.ForeignKey(Location,null=True,blank=True,verbose_name=_(u'location'))    
    
    adresse = models.TextField(_(u'address'),null=True,blank=True)
    ville = models.CharField(_(u'city'),null=True,blank=True, max_length=100)
    code_postal = models.CharField(_(u'zip code'),null=True,blank=True, max_length=5)
    
    telephone_fixe = models.CharField(_(u'land line'),null=True,blank=True, max_length=14)
    telephone_portable = models.CharField(_(u'mobile phone'),null=True,blank=True, max_length=14)
    email = models.EmailField(_(u'personal email'),blank=True)
    email_sha1 = models.CharField(blank=True, max_length=250)
    
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    
    uri = models.CharField(blank=True,max_length=250,verbose_name=_(u'main URI'))    
    
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