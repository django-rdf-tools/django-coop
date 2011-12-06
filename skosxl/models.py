# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
from django.core.urlresolvers import reverse

# Based on SKOS ans SKOS-XL ontologies
# http://www.w3.org/2004/02/skos/core
# http://www.w3.org/2008/05/skos-xl

LABEL_TYPES = Choices(
    ('PrefLabel',    0,  _(u'Preferred label')),
    ('AltLabel',     1,  _(u'Aternative label')),
    ('HiddenLabel',  2,  _(u'Hidden label')),
)

REL_TYPES = Choices(
    ('broaderTransitive',   0,  _(u'Has a broader (transitive) concept')),
    ('narrowerTransitive',  1,  _(u'Has a narrower (transitive) concept')),
    ('related',             2,  _(u'Has a related concept')),    
    ('broader',             3,  _(u'Has a broader concept')),
    ('narrower',            4,  _(u'Has a narrower concept')),
)

MATCH_TYPES = Choices(
    ('exactMatch',   0,  _(u'Matches exactly')),
    ('closeMatch',   1,  _(u'Matches closely')),
    ('broadMatch',   2,  _(u'Has a broader match')),
    ('narrowMatch',  3,  _(u'Has a narrower match')),
    ('relatedMatch', 4,  _(u'Has a related match')),    
)


LANG_LABELS = (
    ('fr',_(u'French')),
    ('en',_(u'English')),
    ('es',_(u'Spanish')),
    ('it',_(u'Italian')),
    ('pt',_(u'Portuguese'))
)

# Le terme c'est le "tag" brut
# Le but c'est de pouvoir appeler tag.concept

#manque le conceptscheme (une ou deux instances)

# Ajouter un field preflabel toujours synchronisé pour le concept (un skos:prefLabel classique...)

class Concept(models.Model):
    definition = models.TextField(_(u'Definition'), blank=True)
    changenote = models.TextField(_(u'Change note'),blank=True)
    created = exfields.CreationDateTimeField(_(u'created'))
    modified = exfields.ModificationDateTimeField(_(u'modified'))
    author = models.CharField(_(u'Author'),blank=True, max_length=250)
    pref_label = models.CharField(_(u'Preferred label'),blank=True,max_length=255) #skos:prefLabel classique
    sem_relations = models.ManyToManyField( "self",symmetrical=False,
                                            through='SemRelation',
                                            verbose_name=(_(u'Semantic relations')))
    def __unicode__(self):
        return self.pref_label
        # preflabel = Label.objects.get(concept=self,type=LABEL_TYPES.PrefLabel,
        #                             term__language='@fr')[0].term.literal#ça devrait être un get(), d'abord assurer un et un seul preflabel
        # return unicode(preflabel).capitalize()
    def save(self, *args, **kwargs):
        try:
            linked_label = Label.objects.get(   concept=self,
                                                type=LABEL_TYPES.PrefLabel,
                                                term__language='fr')
            label = unicode(linked_label.term.literal)
        except Label.DoesNotExist:
            label = None
        self.pref_label = label
        super(Concept, self).save(*args, **kwargs)    
    
class Term(models.Model):
    '''
    Base class for a simple Tag model, will be used as a skosxl:Label
    '''
    literal = models.CharField(_(u'Literal Form'),max_length=255)
    slug = exfields.AutoSlugField(populate_from=('literal'))
    language= models.CharField(_(u'Language'),max_length=10, choices=LANG_LABELS, default='fr')
    created = exfields.CreationDateTimeField(_(u'created'))
    modified = exfields.ModificationDateTimeField(_(u'modified'))
    author = models.CharField(_(u'Author'),blank=True, max_length=250, editable=False)
    concept = models.ManyToManyField(Concept,through='Label', verbose_name=(_(u'Concept')))
    occurences = models.IntegerField(_(u'Occurrences'),default=0)
    def get_absolute_url(self):
        return reverse('tag_detail', args=[self.slug])
    def __unicode__(self):
        return unicode(self.literal)
    # def save(self):
    #     self.author =     comment on récupère le current user
    #createConcept from Term -> pas automatique , demande une revue
    class Meta: 
        verbose_name = _(u'Term')
        verbose_name_plural = _(u'Terms')
    def save(self, *args, **kwargs):
        if self.initiative_set.exists():
            self.count = self.initiative_set.all().count()
        super(Term, self).save(*args, **kwargs)
        

class Vocabulary(models.Model):
    '''
    A remote SKOS Thesaurus
    '''
    name = models.CharField(_(u'Name'),max_length=100)
    info_url = models.URLField(_(u'URL'),blank=True, verify_exists=False)
    class Meta: 
        verbose_name = _(u'SKOS Thesaurus')
        verbose_name_plural = _(u'SKOS Thesaurii')
    def __unicode__(self):
        return self.name
        
        
class Label(models.Model): #should have been named LabelRelation ...
    '''
    A model linking a RDF literal (the Term class in our django app) to a skos:Concept
    Defines sub-property of skosxl:Label 
    '''
    term = models.ForeignKey(Term, verbose_name=(_(u'Term')))         
    concept = models.ForeignKey(Concept, related_name="labels", verbose_name=(_(u'Concept')))
    type = models.PositiveSmallIntegerField( _(u'Type of label'),
                                                    choices=LABEL_TYPES.CHOICES, 
                                                    default=LABEL_TYPES.PrefLabel)
    # a la sauvergarde, verifier qu'il n'y a qu'un preflabel par langue                                      
    class Meta: 
        verbose_name = _(u'Label')
        verbose_name_plural = _(u'Labels')

class SemRelation(models.Model):
    '''
    A model linking two skos:Concept
    Defines a sub-property of skos:semanticRelation property from the origin concept to the target concept
    '''
    origin_concept = models.ForeignKey(Concept,related_name='rel_origin',verbose_name=(_(u'Origin')))
    target_concept = models.ForeignKey(Concept,related_name='rel_target',verbose_name=(_(u'Target')))
    type = models.PositiveSmallIntegerField( _(u'Type of semantic relation'),
                                                    choices=REL_TYPES.CHOICES, 
                                                    default=REL_TYPES.narrowerTransitive)
    class Meta: 
        verbose_name = _(u'Semantic relations')
        verbose_name_plural = _(u'Semantic relations')
        

        
class MapRelation(models.Model):
    origin_concept = models.ForeignKey(Concept,related_name='map_origin',verbose_name=(_(u'Local concept to map')))
    #target_concept = models.ForeignKey(Concept,related_name='map_target',verbose_name=(_(u'Remote concept')),blank=True, null=True)
    target_label = models.CharField(_(u'Preferred label'),max_length=255)#nan nan il faut un autre concept stocké dans un scheme
    uri = models.CharField(_(u'Concept URI'), max_length=250)
    voc = models.ForeignKey(Vocabulary, verbose_name=(_(u'SKOS Thesaurus')))
    match_type = models.PositiveSmallIntegerField( _(u'Type of mapping relation'),
                                                    choices=MATCH_TYPES.CHOICES, 
                                                    default=MATCH_TYPES.exactMatch)
    class Meta: 
        verbose_name = _(u'Mapping relation')
        verbose_name_plural = _(u'Mapping relations')
    

