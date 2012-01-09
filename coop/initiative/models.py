# -*- coding:utf-8 -*-
from django.db import models
from extended_choices import Choices

from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from coop_geo.models import AreaLink,Located
from skosxl.models import LabelledItem
from django.contrib.contenttypes import generic
from taggit_autocomplete_modified.managers \
    import TaggableManagerAutocomplete as TaggableManager
import sorl

class BaseRole(models.Model):
    label = models.CharField(_(u'label'),max_length=60)
    slug = exfields.AutoSlugField(populate_from=('label'))
    class Meta:
        abstract = True
        ordering = ['label']
    def __unicode__(self):
        return unicode(self.label)
    def get_absolute_url(self):
        return reverse('role_detail', args=[self.slug])
   

RELATIONS = Choices(
    ('MEMBER',          1,  _(u' is member of ')),
    ('REG_SUPPLIER',    2,  _(u' has for regular supplier ')),
    ('OCC_SUPPLIER',    3,  _(u' has for casual supplier ')),
    ('SUPPORT',         4,  _(u' received technical support from ')),
    ('FUNDING',         5,  _(u' received financial support from ')),
)

class BaseRelation(models.Model):
    source = models.ForeignKey('coop_local.Initiative', verbose_name=_(u'source organization'),related_name='source')
    target = models.ForeignKey('coop_local.Initiative', verbose_name=_(u'target organization'),related_name='target')
    reltype = models.PositiveSmallIntegerField('Type de relation', choices=RELATIONS.CHOICES)
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    confirmed = models.BooleanField(default=False,verbose_name=_(u'confirmed by the target organization'))
    class Meta:
        abstract = True
    # def rel_label(self):
    #     rel_labels = {
    #         RELATIONS.MEMBER : _(u' is member of '),
    #         RELATIONS.REG_SUPPLIER : _(u' has for regular supplier '),
    #         RELATIONS.OCC_SUPPLIER : _(u' has for casual supplier '),
    #         RELATIONS.SUPPORT : _(u' received technical support from '),
    #         RELATIONS.FUNDING : _(u' received financial support from '),
    #     }
    #     return  unicode(rel_labels[self.reltype])
    def __unicode__(self):    
        return u'"' + self.source.__unicode__() + u'"' + \
            unicode(RELATIONS.CHOICES_DICT[self.reltype]) + \
            u'"' + self.target.__unicode__() + u'".'
    '''
    def save(self):
        vérifier si la relation inverse existe
    '''
    

class BaseEngagement(models.Model):
    membre = models.ForeignKey('coop_local.Membre', verbose_name=_(u'member'),related_name='engagements')
    initiative = models.ForeignKey('coop_local.Initiative',verbose_name=_(u'organization'))
    role = models.ForeignKey('coop_local.Role',verbose_name=_(u'role'))
    fonction = models.CharField(blank=True, max_length=100)
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    uri = models.CharField(_(u'main URI'),blank=True, max_length=250, editable=False)
    uuid = exfields.UUIDField() #nécessaire pour URI de l'engagement
    class Meta:
        abstract = True
    '''
    def save(self):
        ramener URI du membre / mais D2R peut bien linker le champ de membre ?
    '''    

class BaseOrganizationCategory(models.Model):
    label = models.CharField(blank=True, max_length=100)
    slug = exfields.AutoSlugField(populate_from=('label'))
    class Meta:
        abstract = True
        verbose_name = _(u'organization category')
        verbose_name_plural = _(u'organization categories')
    def __unicode__(self):
        return self.label

class BaseInitiative(models.Model):
    title       = models.CharField(_('title'),max_length=250)
    acronym     = models.CharField(_('acronym'),blank=True,null=True,max_length=250)
    description = models.TextField(_(u'description'),blank=True,null=True)
    uri         = models.CharField(_(u'main URI'),blank=True,null=True, max_length=250, editable=False)
    
    logo = sorl.thumbnail.ImageField(upload_to='logos/',null=True,blank=True)
    
    tags = TaggableManager(through=LabelledItem, blank=True)

    relations = models.ManyToManyField('coop_local.Initiative',symmetrical=False,through='coop_local.Relation',verbose_name=_(u'relations'))

    category = models.ManyToManyField('coop_local.OrganizationCategory', blank=True, null=True, verbose_name=_(u'category'))

    members     = models.ManyToManyField('coop_local.Membre',through='coop_local.Engagement',verbose_name=_(u'members'))
    telephone_fixe = models.CharField(_(u'land line'),blank=True,null=True, max_length=14)
    mobile = models.CharField(_(u'mobile phone'),blank=True,null=True, max_length=14)
    
    located = generic.GenericRelation(Located)
    area = generic.GenericRelation(AreaLink)
    
    #action_area = models.ForeignKey(Area, verbose_name=_(u'impact Area'), blank=True, null=True)
    
    birth = models.DateField(null=True, blank=True)
    email   = models.EmailField(_(u'global email'),blank=True,null=True)
    web     = models.URLField(_(u'web site'),blank=True,null=True, verify_exists=False)
    rss     = models.URLField(_(u'RSS feed'),blank=True,null=True, verify_exists=False)
    
    vcal    = models.URLField(_(u'vCal'),blank=True,null=True, verify_exists=True)
    
    slug    = exfields.AutoSlugField(populate_from='title',blank=True)
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    active  = models.BooleanField(default=True, verbose_name=_(u'active'))
    notes   = models.TextField(blank=True, verbose_name=_(u'notes'))
    class Meta:
        abstract = True
        ordering = ['title']
    def __unicode__(self):
        if(self.acronym != None and len(self.title) > 40):
            return unicode(self.acronym)
        else:
            return unicode(self.title)
    def has_location(self):
        return self.located.all().count()>0
    has_location.boolean = True    
    has_location.short_description = _(u'geo')
    def has_description(self):
        return self.description is not None
    has_description.boolean = True    
    has_description.short_description = _(u'desc.')
    #@models.permalink
    def get_absolute_url(self):
        return reverse('initiative_detail', args=[self.slug])
        
       # return ('/initiative/'+self.slug+'.html')
    def get_tags(self):
        return self.tags.all()
        
    def get_relations(self):
        relations = {}
        relmap = RELATIONS.REVERTED_CHOICES_CONST_DICT
        
        for rel in self.source.all():
            reltype = str('OUT_' + relmap[rel.reltype])# les relations de moi vers les autres
            if reltype not in relations :
                relations[reltype] = []
            relations[reltype].append(rel.target)
        for rel in self.target.all():
            reltype = str('IN_' + relmap[rel.reltype])# les relations déclarées par les autres
            if reltype not in relations :
                relations[reltype] = []
            if rel.confirmed:# et confirmées
                relations[reltype].append(rel.source)
        return relations
        
    def local_uri(self):
        return ('http://dev.credis.org:8000/initiative/'+self.slug+'/')




