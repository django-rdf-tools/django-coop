# -*- coding:utf-8 -*-
from django.db import models
from extended_choices import Choices
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from coop_geo.models import AreaLink,Located
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
import sorl
from django.core.exceptions import ValidationError

DISPLAY = Choices(
    ('PUBLIC',  1,  _(u'public information')),
    ('USERS',   2,  _(u'registered users')),
    ('MEMBER',  3,  _(u'members of an organization')),
    ('RELATED', 4,  _(u'related organizations members')),
    ('ORG',     5,  _(u'members of this organization')),
    ('ADMIN',   6,  _(u'administrators of this site')),
)

# will apply to contact numbers and 

COMM_MEANS = Choices(
    ('LAND',    1,  _(u'Landline phone')),
    ('GSM',     2,  _(u'Mobile phone')),
    ('FAX',     3,  _(u'Fax')),
    ('SKYPE',   4,  _(u'Skype')),
    ('TWITTER', 5,  _(u'Twitter')),
)

class BaseContact(models.Model):
    category        = models.PositiveSmallIntegerField(_(u'Category'), choices=COMM_MEANS.CHOICES)
    content         = models.CharField(_(u'content'),max_length=100)
    details         = models.CharField(_(u'details'),blank=True, max_length=100)
    display         = models.PositiveSmallIntegerField(_(u'Display'), choices=DISPLAY.CHOICES, default=DISPLAY.PUBLIC)
    created         = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified        = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    content_type    = models.ForeignKey(ContentType, blank=True, null=True)
    object_id       = models.PositiveIntegerField()
    content_object  = generic.GenericForeignKey('content_type', 'object_id')
    class Meta:
        abstract = True
        ordering = ['category']
        verbose_name = _(u'Contact')
        verbose_name_plural = _(u'Contacts')
    def __unicode__(self):
        return self.content

    def clean(self):
        if self.category in [1,2,3]:
            import re
            phoneSplitRegex = re.compile(r"[\-\(\) \.\,]")         
            parts = phoneSplitRegex.split(self.content)
            num = ''.join(parts)
            if len(num) == 10:
                self.content = '.'.join((num[:2],num[2:4],num[4:6],num[6:8],num[8:]))
            else:
                raise ValidationError(_(u'Phone numbers must have 10 digits'))
    def save(self, *args, **kwargs):
        self.clean()
        super(BaseContact, self).save(*args, **kwargs) 
        
        


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
    reltype = models.PositiveSmallIntegerField(_(u'Relation type'), choices=RELATIONS.CHOICES)
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
    membre = models.ForeignKey('coop_local.Membre', verbose_name=_(u'member'),related_name='engagements')   #TODO name
    initiative = models.ForeignKey('coop_local.Initiative',verbose_name=_(u'organization'))                 #TODO name
    role = models.ForeignKey('coop_local.Role',verbose_name=_(u'role'))
    fonction = models.CharField(blank=True, max_length=100, verbose_name=_(u'detailed role'))               #TODO name
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    uri = models.CharField(_(u'main URI'),blank=True, max_length=250, editable=False)
    uuid = exfields.UUIDField() #nécessaire pour URI de l'engagement
    class Meta:
        abstract = True
        verbose_name = _('Engagement')
        verbose_name_plural = _('Engagements')
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

class BaseInitiative(models.Model): # TODO => BaseOrganization
    title       = models.CharField(_(u'title'),max_length=250)
    acronym     = models.CharField(_(u'tagline'),blank=True,null=True,max_length=250) #TODO => tagline
    
    description = models.TextField(_(u'description'),blank=True,null=True)
    uri         = models.CharField(_(u'main URI'),blank=True,null=True, max_length=250, editable=False)
    
    logo = sorl.thumbnail.ImageField(upload_to='logos/',null=True,blank=True)
    
    relations = models.ManyToManyField('coop_local.Initiative',symmetrical=False,through='coop_local.Relation',verbose_name=_(u'relations'))

    category = models.ManyToManyField('coop_local.OrganizationCategory', blank=True, null=True, verbose_name=_(u'category'))

    members = models.ManyToManyField('coop_local.Membre',through='coop_local.Engagement',verbose_name=_(u'members'))
    telephone_fixe = models.CharField(_(u'land line'),blank=True,null=True, max_length=14) 
    mobile = models.CharField(_(u'mobile phone'),blank=True,null=True, max_length=14)
    
    located = generic.GenericRelation(Located)
    area    = generic.GenericRelation(AreaLink)
    contact = generic.GenericRelation('coop_local.Contact')
        
    birth = models.DateField(_(u'creation date'),null=True, blank=True)
    email   = models.EmailField(_(u'global email'),blank=True,null=True)
    web     = models.URLField(_(u'web site'),blank=True,null=True, verify_exists=False)
    rss     = models.URLField(_(u'RSS feed'),blank=True,null=True, verify_exists=False)
    vcal    = models.URLField(_(u'vCalendar'),blank=True,null=True, verify_exists=True)
    
    slug    = exfields.AutoSlugField(populate_from='title',blank=True)
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    active  = models.BooleanField(_(u'active'),default=True,)
    notes   = models.TextField(_(u'notes'),blank=True)
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
        return len(self.description) > 20
    has_description.boolean = True    
    has_description.short_description = _(u'desc.')
    
    #@models.permalink
    def get_absolute_url(self):
        return reverse('initiative_detail', args=[self.slug])
        
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




