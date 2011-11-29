# -*- coding:utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
from coop.membre.models import BaseMembre
from coop.place.models import BaseSite
#from coop.agenda.models import BaseCalendar, BaseEvent
from coop.exchange.models import BaseExchange, BaseTransaction
from coop.initiative.models import BaseInitiative,BaseEngagement,BaseRole


# Personnaliser vos modèle ici en ajoutant les champs nécessaires
# exemple : personnalisation CREDIS

class Engagement(BaseEngagement):
    pass

class Membre(BaseMembre):
    adherent = models.NullBooleanField(default=False)
    batisseur = models.BooleanField(default=False)

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
)

# class Calendar(BaseCalendar):
#     pass
# 
# class Event(BaseEvent):
#     pass

class Exchange(BaseExchange):
    pass

class Transaction(BaseTransaction):
    pass

class Site(BaseSite):
    pass

class Initiative(BaseInitiative):
    siret = models.CharField('Numero SIRET',blank=True, null=True, max_length=20)
    naf = models.CharField('Code d’activité NAF',blank=True, null=True, max_length=10)
    presage = models.CharField('Numero PRESAGE',blank=True, null=True, max_length=10)
    statut = models.PositiveSmallIntegerField('Statut juridique',
                                                choices=STATUTS.CHOICES, 
                                                  default=STATUTS.ASSO)
    secteur_fse = models.PositiveSmallIntegerField('Secteur d’activité FSE',
                                                    choices=SECTEURS_FSE.CHOICES, 
                                                    default=SECTEURS_FSE.TOUS)

