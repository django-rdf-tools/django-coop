# -*- coding:utf-8 -*-
from django.conf import settings
if 'haystack' in settings.INSTALLED_APPS:
    from haystack import indexes
    from coop_local.models import Organization, Exchange, Article, Event



    if getattr(settings, 'HAYSTACK_REALTIME', False):
        Indexes = indexes.RealTimeSearchIndex
    else:
        Indexes = indexes.SearchIndex


    # The main class
    class CoopIndex(Indexes):
        text = indexes.CharField(document=True, use_template=True)
        tags = indexes.MultiValueField(boost=1.2, faceted=True)
        # modified = indexes.DateField(model_attr='modified', faceted=True)
        rendered = indexes.CharField(use_template=True, indexed=False)
        sites = indexes.MultiValueField()


        def prepare_sites(self, obj):
            return [u"%s" % site.domain for site in obj.sites.all()]

        def prepare_tags(self, obj):
            return [u"%s" % tag.name for tag in obj.tags.all()]

        def prepare(self, obj):
            print "prepare id=%s %s" % (obj.id, obj)
            prepared_data = super(CoopIndex, self).prepare(obj)

            prepared_data['text'] = prepared_data['text'] + ' ' + \
            ' '.join(prepared_data['tags']) 
            return prepared_data


    # The main class
    class CoopIndexWithoutSite(Indexes):
        text = indexes.CharField(document=True, use_template=True)
        tags = indexes.MultiValueField(boost=1.2, faceted=True)
        # modified = indexes.DateField(model_attr='modified', faceted=True)
        rendered = indexes.CharField(use_template=True, indexed=False)

        def prepare_tags(self, obj):
            return [u"%s" % tag.name for tag in obj.tags.all()]

        def prepare(self, obj):
            print "prepare id=%s %s" % (obj.id, obj)
            prepared_data = super(CoopIndexWithoutSite, self).prepare(obj)

            prepared_data['text'] = prepared_data['text'] + ' ' + \
            ' '.join(prepared_data['tags']) 
            return prepared_data


    class OrganizationIndex(CoopIndex):

        def get_model(self):
            return Organization


    class ExchangeIndex(CoopIndex):
        product = indexes.MultiValueField(boost=1.2, faceted=True)

        def prepare_product(self, obj):
            return [u"%s" % prod.title for prod in obj.products.all()]

        def prepare(self, obj):
            # print "prepare %s" % obj
            prepared_data = super(CoopIndex, self).prepare(obj)
            prepared_data['text'] = prepared_data['text'] + ' ' + \
            ' '.join(prepared_data['product']) 
            return prepared_data

        def get_model(self):
            return Exchange


    class ArticleIndex(CoopIndex):

        def get_model(self):
            return Article


    class EventIndex(CoopIndex):

        def get_model(self):
            return Event







