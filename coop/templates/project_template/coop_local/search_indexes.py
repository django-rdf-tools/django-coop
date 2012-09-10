# -*- coding:utf-8 -*-

# TODO : est-ce qu'on peut proposer des valeurs par defaut ici ?
# ou deriver d'index pre-existants et leur ajouter quelques champs secifiques au site ?

import datetime
from haystack import indexes, site
from coop_local.models import Organization


class OrganizationIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    acronym = indexes.CharField(model_attr='subtitle')
    description = indexes.CharField(model_attr='description')
    tags = indexes.MultiValueField()

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

site.register(Organization, OrganizationIndex)