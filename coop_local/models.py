# -*- coding:utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
from coop.person.models import BasePerson,BasePersonCategory
#from coop.agenda.models import BaseCalendar, BaseEvent
from coop.exchange.models import BaseExchange, BaseTransaction, BasePaymentModality
from coop.initiative.models import BaseOrganizationCategory,BaseInitiative,BaseRelation,BaseEngagement,BaseRole, BaseContact
from coop.link.models import BaseSemLink


# Personnaliser vos modèle ici en ajoutant les champs nécessaires

class Engagement(BaseEngagement):
    pass

class Relation(BaseRelation):
    pass

class MemberCategory(BasePersonCategory):
    pass

class Membre(BasePerson):
    pass

class Role(BaseRole):
    pass

SECTEURS_FSE = Choices(
    ('TOUS',        0,  'Tous secteurs d’activité'),
    ('EQUITABLE',   1,  'Commerce équitable de biens et services'),
    ('OFFLINE',     2,  'Culture, loisirs, sport'),
    ('TOURISME',    3,  'Eco-tourisme'),
    ('ENV',         4,  'Environnement, énergies renouvelable'),
    ('TIC',         5,  'Information et Communication'),
    ('TRANSPORT',   6,  'Transport,mobilité'),
    ('SERVICE',     7,  'Services aux personnes'),
    ('AUTRE',       8,  'Autres activités')
)

STATUTS = Choices(
    ('ASSO',    1,  'Association de loi 1901'),
    ('SCOP',    2,  'Société Coopérative Ouvrière de Production'),
    ('SCIC',    3,  'Société Coopérative d’Intérêt Collectif'),
    ('COOP47',  4,  'Société Coopérative de loi 1947'),
    ('EPCI',    5,  'Collectivité territoriale'),    
)

# class Calendar(BaseCalendar):
#     pass
# 
# class Event(BaseEvent):
#     pass


from coop_tag.models import CtaggedItem
from taggit_autosuggest.managers import TaggableManager

class Exchange(BaseExchange):
    tags = TaggableManager( through=CtaggedItem, 
                            help_text="Une liste de mots-clés séparés par des virgules",
                            blank=True, verbose_name='Mots-clés')
    

class PaymentModality(BasePaymentModality):
    pass

class Transaction(BaseTransaction):
    pass

class OrganizationCategory(BaseOrganizationCategory):
    pass


class Initiative(BaseInitiative):
    siret = models.CharField('Numero SIRET',blank=True, null=True, max_length=20)
    naf = models.CharField('Code d’activité NAF',blank=True, null=True, max_length=10)
    presage = models.CharField('Numero PRESAGE',blank=True, null=True, max_length=10)
    
    tags = TaggableManager( through=CtaggedItem, 
                            help_text="Une liste de mots-clés séparés par des virgules",
                            blank=True, verbose_name='Mots-clés')
    
    statut = models.PositiveSmallIntegerField('Statut juridique',
                                                choices=STATUTS.CHOICES, 
                                                  default=STATUTS.ASSO)
    secteur_fse = models.PositiveSmallIntegerField('Secteur d’activité FSE',
                                                    choices=SECTEURS_FSE.CHOICES, 
                                                    default=SECTEURS_FSE.TOUS)
                                                    


class SeeAlsoLink(BaseSemLink):
    class Meta:
        verbose_name = _(u'SeeAlso link')
        verbose_name_plural = _(u'SeeAlso links')
    
class SameAsLink(BaseSemLink):
    class Meta:
        verbose_name = _(u'SameAs link')
        verbose_name_plural = _(u'SameAs links')

class Contact(BaseContact):
    pass


from coop_cms.models import BaseArticle
from django.contrib.auth.models import User

class Article(BaseArticle):
    author = models.ForeignKey(User, blank=True, default=None, null=True)
    
    def can_publish_article(self, user):
        return (self.author == user)
        
    #def can_edit_article(self, user):
    #    return True
    #


#Patching our custom Article to add a backward generic relation with events (use in templates)
from django.contrib.contenttypes import generic
from coop_local.models import Article
from coop_local.models import Initiative
from coop_agenda.models import Event

if not hasattr(Article, "events"):
    e = generic.GenericRelation(Event)
    e.contribute_to_class(Article, "events")

if not hasattr(Initiative, "events"):
    e = generic.GenericRelation(Event)
    e.contribute_to_class(Initiative, "events")


