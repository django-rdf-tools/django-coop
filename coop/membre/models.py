# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.contrib.contenttypes import generic
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

from coop.initiative.models import DISPLAY

class BaseMembre(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, unique=True,verbose_name=_(u'django user'),editable=False)
    username = models.CharField(blank=True, max_length=100, unique=True)    
    #pour D2RQ et poura voir des URI clean meme pour des non-users
    
    category = models.ManyToManyField('coop_local.MemberCategory', blank=True, null=True, verbose_name=_(u'category'))
    last_name = models.CharField(_(u'last name'),max_length=100)
    first_name = models.CharField(_(u'first name'),max_length=100,null=True,blank=True)
    location = models.ForeignKey(Location,null=True,blank=True,verbose_name=_(u'location'))    
    location_display = models.PositiveSmallIntegerField(_(u'Display'), choices=DISPLAY.CHOICES, default=DISPLAY.PUBLIC)
    contact = generic.GenericRelation('coop_local.Contact')
    email = models.EmailField(_(u'personal email'),blank=True)
    email_sha1 = models.CharField(blank=True, max_length=250)
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    uri = models.CharField(blank=True,max_length=250,verbose_name=_(u'main URI'))    
    notes   = models.TextField(blank=True, verbose_name=_(u'notes'))
    structure = models.CharField(blank=True, max_length=100)

    class Meta:
        abstract = True
        verbose_name = _(u'Personne')
        verbose_name_plural = _(u'Personnes')
    def __unicode__(self):
        return self.first_name+u' '+self.last_name
        
    @models.permalink
    def get_absolute_url(self):
        #return reverse('profiles_profile_detail', args=[self.username])
        return ('profiles_profile_detail', (), {'username': self.username })
        
    def has_user_account(self):
        return (self.user != None)
    has_user_account.boolean = True    
    has_user_account.short_description = _(u'django account')
    
    def has_role(self):
        return (self.engagements.count()>0 )
    has_role.boolean = True    
    has_role.short_description = _(u'has organization')
    
        
    def engagements(self):
        eng = []
        for e in self.engagement_set.all():
            eng.append({'initiative':e.initiative,'role':e.role})
        return eng
    def init_uri(self):
        return 'http://' + Site.objects.get_current().domain + '/webid/' + self.username + '/'
    
    def save(self, *args, **kwargs):
        # create username slug if not set
        if self.username == '':
            newname = slugify(self.first_name).replace('-','_')+'.'+\
                        slugify(self.last_name).replace('-','_')
            self.username = newname
        # synchronize fields with django User model
        if self.user:
            chg = False
            for field in ('username','first_name','last_name','email'):
                if(getattr(self.user,field) != getattr(self,field)):
                    setattr(self.user, field, getattr(self,field))
                    chg = True
            if(chg) : self.user.save()
        # create / update URI           
        if self.uri != self.init_uri():
            self.uri = self.init_uri()
        super(BaseMembre, self).save(*args, **kwargs)    
        
