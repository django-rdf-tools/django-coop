# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from skosxl.models import Term
from django.core.urlresolvers import reverse
from coop_geo.models import Area


class BaseRole(models.Model):
    label = models.CharField(_(u'Intitulé'),max_length=30)
    slug = exfields.AutoSlugField(populate_from=('label'))
    class Meta:
        abstract = True
    def __unicode__(self):
        return unicode(self.label)
    def get_absolute_url(self):
        return reverse('role_detail', args=[self.slug])
    

class BaseEngagement(models.Model):
    membre = models.ForeignKey('coop_local.Membre')
    initiative = models.ForeignKey('coop_local.Initiative')
    role = models.ForeignKey('coop_local.Role')
    created = exfields.CreationDateTimeField(_(u'Création'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'Modification'),null=True)
    #membre_uri = models.CharField(_(u'Profil FOAF'),blank=True, max_length=250, editable=False)
    uuid = exfields.UUIDField() #nécessaire pour URI de l'engagement
    class Meta:
        abstract = True
            
    '''
    def save(self):
        ramener URI du membre / mais D2R peut bien linker le champ de membre ?
    '''    

class BaseInitiative(models.Model):
    title = models.CharField(_('title'),max_length=250)
    acronym = models.CharField(_('acronym'),blank=True,null=True,max_length=250)
    description = models.TextField(_(u'description'),blank=True,null=True)
    uri = models.CharField(_(u'main URI'),blank=True,null=True, max_length=250, editable=False)
    
    tags = models.ManyToManyField(Term)

    members = models.ManyToManyField('coop_local.Membre',through='coop_local.Engagement',verbose_name=_(u'members'))
    
    telephone_fixe = models.CharField(_(u'land line'),blank=True,null=True, max_length=14, editable=False)
    
    action_area = models.ForeignKey(Area, verbose_name=_(u'Impact Area'), blank=True, null=True)
    
    # date_birth = 
    
    email = models.EmailField(_(u'Email général'),blank=True,null=True)
    web = models.URLField(_(u'Site web'),blank=True,null=True, verify_exists=True)
    rss = models.URLField(_(u'Flux RSS'),blank=True,null=True, verify_exists=True)
    slug = exfields.AutoSlugField(populate_from='title',blank=True,null=True)#TODO enlever null ensuite
    created = exfields.CreationDateTimeField(_(u'Création'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'Modification'),null=True)
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    class Meta:
        abstract = True
    def __unicode__(self):
        if(self.acronym != None and len(self.title) > 40):
            return unicode(self.acronym)
        else:
            return unicode(self.title)
        
    #@models.permalink
    def get_absolute_url(self):
        return reverse('initiative_detail', args=[self.slug])
        
       # return ('/initiative/'+self.slug+'.html')
    def get_tags(self):
        return self.tags.all()
        
    def local_uri(self):
        return ('http://dev.credis.org:8000/initiative/'+self.slug+'/')





   
    
    