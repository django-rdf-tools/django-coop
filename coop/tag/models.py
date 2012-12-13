# -*- coding:utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
import rdflib


if 'coop_tag' in settings.INSTALLED_APPS:
    from coop_tag.models import TagBase, GenericTaggedItemBase, TaggedItemBase
    from coop.models import URIModel
    # in coop_settings, TAGGER_TAG_MODEL = 'coop_local.Tag'

    class CoopTaggedItem(GenericTaggedItemBase, TaggedItemBase):
        #tag = models.ForeignKey('coop_local.Tag', related_name="%(app_label)s_%(class)s_taggeditem_items")

        class Meta:
            verbose_name = _(u'tagged item')
            verbose_name_plural = _(u'tagged items')
            abstract = True
            app_label = "coop_local"

    class CoopTag(TagBase, URIModel):
        # Fields name and slug are defined in TagBase

        language = models.CharField(_(u'language'), max_length=10, default='fr')
        person = models.ForeignKey('coop_local.Person', blank=True, null=True, verbose_name=_(u'person'), editable=False)
        person_uri = models.CharField(_(u'person URI'), blank=True, max_length=250, editable=False)

        # Thesaurus link
        concept_uri = models.CharField(_(u'Concept URI'), blank=True, max_length=250, editable=False)

        # Tags have a common uri domain
        domain_name = 'thess.economie-solidaire.fr'

        @property
        def uri_id(self):
            return self.slug

        def label(self):
            return self.name

        def get_absolute_url(self):
            return reverse('tag_detail', args=[self.slug])

        class Meta:
            verbose_name = _(u'tag')
            verbose_name_plural = _(u'tags')
            abstract = True
            app_label = "coop_local"

        # RDDF stuff
        rdf_type = settings.NS.skosxl.Label
        base_mapping = [
            ('single_mapping', (settings.NS.dct.created, 'created'), 'single_reverse'),
            ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
            ('single_mapping', (settings.NS.skosxl.literalForm, 'name', None, 'fr'), 'single_reverse'),
            ('single_mapping', (settings.NS.rdfs.label, 'name', None, 'fr'), 'single_reverse'),
            ('single_mapping', (settings.NS.foaf.made, 'person_uri'), 'single_reverse'),
            ('single_mapping', (settings.NS.ess.labelFor, 'concept_uri'), 'single_reverse'),

            ('scheme_mapping', (settings.NS.skos.inScheme, ''), 'scheme_mapping_reverse'),
            ('broader_mapping', (settings.NS.ess.broaderLabel, ''), 'broader_mapping_reverse'),
       ]

        def scheme_mapping(self, rdfPred, djF, datatype=None, lang=None):
            try:
                m = models.get_model('coop_cms', 'navnode')
                nodes = m.objects.filter(object_id=self.id)
            except m.DoesNotExist:
                return []
            res = []
            for node in nodes:
                if  not node.tree.name == 'default':
                    res.append((rdflib.term.URIRef(self.uri), rdfPred, rdflib.term.URIRef(node.tree.uri)))
            return res

        #TODO to be TESTED..... comment ca marche les NavNode, NavTree....
        def scheme_mapping_reverse(self, g, rdfPred, djF, datatype=None, lang=None):
            schemes = list(g.objects(rdflib.term.URIRef(self.uri), rdfPred))
            nodes = models.get_model('coop_cms', 'navnode').objects.filter(object_id=self.id)
            # Un tag peut appartenir a plusieurs schemes
            mNavtree = models.get_model('coop_local', 'Navtree')
            for scheme in schemes:
                sch = mNavtree.objects.get(uri=scheme.toPython())
                for node in nodes:
                    if node.tree.id == sch.id:
                        node.tree = sch
                        node.save()


        def broader_mapping(self, rdfPred, djF, datatype=None, lang=None):
            try:
                m = models.get_model('coop_cms', 'navnode')
                nodes = m.objects.filter(object_id=self.id)
            except m.DoesNotExist:
                return []
            res = []
            for node in nodes:
                try:
                    node_parent = m.objects.get(id=node.parent.id)
                except (m.DoesNotExist, AttributeError):
                    node_parent = None

                if not node_parent == None and  node_parent.content_type.name == 'tag':
                    mTag = models.get_model('coop_local', 'tag')
                    tag_parent = mTag.objects.get(id=node_parent.object_id)
                    res.append((rdflib.term.URIRef(self.uri), rdfPred, rdflib.term.URIRef(tag_parent.uri)))
            return res



        def broader_mapping_reverse(self, g, rdfPred, djF, datatype=None, lang=None):
            pass









