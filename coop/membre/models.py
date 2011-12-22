# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from coop_geo.models import Location
from django.contrib.sites.models import Site

class BaseMemberCategory(models.Model):
    label = models.CharField(blank=True, max_length=100)
    slug = exfields.AutoSlugField(populate_from=('label'))
    class Meta:
        abstract = True
        verbose_name = _(u'Member category')
        verbose_name_plural = _(u'Member categories')
    def __unicode__(self):
        return self.label    

class BaseMembre(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, unique=True,verbose_name=_(u'django user'),editable=False)
    
    category = models.ManyToManyField('coop_local.MemberCategory', blank=True, null=True, verbose_name=_(u'category'))

    nom = models.CharField(_(u'first name'),max_length=100)
    prenom = models.CharField(_(u'last name'),max_length=100,null=True,blank=True)
    pub_name = models.BooleanField(default=False, verbose_name=_(u'publicize name'))
    
    location = models.ForeignKey(Location,null=True,blank=True,verbose_name=_(u'location'))    
    pub_location = models.BooleanField(default=False, verbose_name=_(u'publicize location'))
    
    adresse = models.TextField(_(u'address'),null=True,blank=True)
    ville = models.CharField(_(u'city'),null=True,blank=True, max_length=100)
    code_postal = models.CharField(_(u'zip code'),null=True,blank=True, max_length=5)
    
    telephone_fixe = models.CharField(_(u'land line'),null=True,blank=True, max_length=14)
    pub_phone = models.BooleanField(default=False, verbose_name=_(u'publicize phone'))
    
    telephone_portable = models.CharField(_(u'mobile phone'),null=True,blank=True, max_length=14)
    pub_mobile = models.BooleanField(default=False, verbose_name=_(u'publicize mobile'))
    
    email = models.EmailField(_(u'personal email'),blank=True)
    email_sha1 = models.CharField(blank=True, max_length=250)
    
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    
    uri = models.CharField(blank=True,max_length=250,verbose_name=_(u'main URI'))    
    
    class Meta:
        abstract = True
        verbose_name = _(u'Member')
        verbose_name_plural = _(u'Members')
    def __unicode__(self):
        return self.prenom+u' '+self.nom
    @models.permalink
    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })
    def has_user_account(self):
        return (self.user != None)
    has_user_account.boolean = True    
    has_user_account.short_description = _(u'django account')
    
    def has_role(self):
        return (self.engagements.count()>0 )
    has_role.boolean = True    
    has_role.short_description = _(u'has organization')
    
        
    # def engagements(self):
    #     eng = []
    #     for e in self.engagement_set.all():
    #         eng.append({'initiative':e.initiative,'role':e.role})
    #     return eng
    def init_uri(self):
        if self.user is None:
            return 'http://' + Site.objects.get_current().domain + '/id/membre/' + self.user.username + '/'
        else:
            return ''    
    def save(self, *args, **kwargs):
        if self.uri is None:
            print 'uri vide'
            self.uri = self.init_uri()
        super(BaseMembre, self).save(*args, **kwargs)    
    '''
    def save(self):
        if(self.uri == None):
            set_uri
            linked_notification(self, creation)
        else:
            if(not uri.is_local()):
                linked_notification(self, haschanged ?)
            
            
    '''