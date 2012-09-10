# -*- coding:utf-8 -*-
from django.db import models
from extended_choices import Choices
from coop.org.models import BaseClassification


# Use Choices() !
# ETAT = ((0, 'Inconnu'),
#         (1, 'Active'),
#         (2, 'En sommeil'),
#         (3, 'En projet'),
# )


# Classifications classes must be instantiated manually (no default model)
# uncomment to get a legal status and activity sector classification

# from coop.org.models import BaseClassification

# class Statut(BaseClassification):
#     class Meta:
#         verbose_name = 'statut juridique'
#         verbose_name_plural = 'statuts juridiques'
#         app_label = 'coop_local'

# class Secteur(BaseClassification):
#     class Meta:
#         verbose_name = u"secteur d'activite"
#         verbose_name_plural = u"secteurs d'activite"
#         app_label = 'coop_local'

# If you uncommented one of these models, you should override the Organization model to make a Fkey to them...

