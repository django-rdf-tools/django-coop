# -*- coding:utf-8 -*-

from django.conf import settings
from coop.models import StaticURIModel, URIModel
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
import rdflib
from datetime import datetime

# ----------- Customizing coop-cms Article for more coop intergration

if "coop_cms" in settings.INSTALLED_APPS:

    from coop_cms.models import BaseArticle, BaseNavTree

    class CoopArticle(BaseArticle, StaticURIModel):

        organization = models.ForeignKey('coop_local.Organization', blank=True, null=True,
                                         verbose_name=_('publisher'), related_name='articles')
        person = models.ForeignKey('coop_local.Person', blank=True, null=True,
                                   verbose_name=_(u'author'), related_name='articles')
        # Linking to remote objects
        remote_person_uri = models.URLField(_(u'remote person URI'), blank=True, max_length=255)
        remote_person_label = models.CharField(_(u'remote person label'),
                                               max_length=250, blank=True, null=True,
                                               help_text=_(u'fill this only if the person record is not available locally'))
        remote_organization_uri = models.URLField(_(u'remote organization URI'), blank=True, max_length=255)
        remote_organization_label = models.CharField(_(u'remote organization label'),
                                                     max_length=250, blank=True, null=True,
                                                     help_text=_(u'fill this only if the organization record is not available locally'))

        isSection = models.BooleanField(_(u'Container article'), default=False,
                                        help_text=_(u"Will display a list of links for its children articles"))

        display_dates = models.BooleanField(_(u'Display dates'), default=True,
                                            help_text=_(u"The creation and modification dates will be displayed as meta-data"))

        if "coop.mailing" in settings.INSTALLED_APPS:
            newsletter = models.ForeignKey('coop_local.Newsletter', verbose_name=u'newsletter',
                                blank=True, null=True, related_name='news_article',
                                on_delete=models.SET_NULL)


        if "coop.agenda" in settings.INSTALLED_APPS:
            dated = generic.GenericRelation('coop_local.Dated')
            occurences = generic.GenericRelation('coop_local.GenericDate')

            def upcoming_occurrences(self):
                """
                Return all occurrences that are set to start on or after the current
                time.
                """
                return self.occurences.all().filter(start_time__gte=datetime.now())

            def next_occurrence(self):
                """
                Return the single occurrence set to start on or after the current time
                if available, otherwise ``None``.
                """
                upcoming = self.upcoming_occurrences()
                return upcoming and upcoming[0] or None

            def daily_occurrences(self, dt=None):
                """
                Convenience method wrapping ``GenericDate.objects.daily_occurrences``.
                """
                return get_model('coop_local', 'GenericDate').objects.daily_occurrences(dt=dt, article_id=self.pk)


        if "coop.doc" in settings.INSTALLED_APPS:
            attachments = generic.GenericRelation('coop_local.Attachment')

        external_links = generic.GenericRelation('coop_local.Link')


        def label(self):
            return self.title

        def save(self, *args, **kwargs):
            self.active = (self.publication == BaseArticle.PUBLISHED)
            super(CoopArticle, self).save(*args, **kwargs)

        # def can_publish_article(self, user):
        #     return (self.author == user)

        #def can_edit_article(self, user):
        #   return True
        #   test on URI, not on django user

        class Meta:
            verbose_name = _(u"article")
            verbose_name_plural = _(u"articles")
            abstract = True
            app_label = 'coop_local'
            ordering = ['-modified']

        # RDF stuff
        def isOpenData(self):
            return not self.isSection and self.publication == BaseArticle.PUBLISHED

        @property
        def description(self):
            return self.summary

        rdf_type = settings.NS.dcmi.Text
        base_mapping = [
            ('single_mapping', (settings.NS.dct.created, 'created'), 'single_reverse'),
            ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
            ('single_mapping', (settings.NS.dct.title, 'title'), 'single_reverse'),
            ('single_mapping', (rdflib.URIRef(str(settings.NS['dct']) + 'abstract'), 'summary'), 'single_reverse'),  # bug in rdflib
            ('single_mapping', (settings.NS.dct.description, 'content'), 'single_reverse'),
            # ('single_mapping', (settings.NS.dce.type, 'rdf_type'), ''),  # DC compliance

            ('local_or_remote_mapping', (settings.NS.dct.creator, 'person'), 'local_or_remote_reverse'),
            ('local_or_remote_mapping', (settings.NS.dct.publisher, 'organization'), 'local_or_remote_reverse'),

            ('multi_mapping', (settings.NS.dct.subject, 'tags'), 'multi_reverse'),
                        ]


# ----------- Idem for coop-cms NavTree            

    class CoopNavTree(BaseNavTree, URIModel):

        class Meta:
            verbose_name = _(u'Navigation tree')
            verbose_name_plural = _(u'Navigation trees')
            abstract = True
            app_label = 'coop_local'

        # RDF stuffs

        # As the "default" NavTree should NOT be exort as rdf data
        # A Nice solution is overwritte toRdfGraph method
        def isOpenData(self):
            return not (self.name == 'default' or self.name == 'spip')
 
        rdf_type = settings.NS.skos.ConceptScheme
        base_mapping = [
            ('single_mapping', (settings.NS.dct.created, 'created'), 'single_reverse'),
            ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
            ('single_mapping', (settings.NS.rdfs.label, 'name'), 'single_reverse'),
        ]


    



