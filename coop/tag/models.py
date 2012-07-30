# -*- coding:utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings

if 'coop_tag' in settings.INSTALLED_APPS:
    from coop_tag import TagBase
    from coop.models import URIModel

    # WARNING = in coop_settings, TAG_MODEL = ('coop_local', 'Tag')

    class Tag(TagBase, URIModel):
        '''
        Defines a Tag resource
        '''
        # Fields name and slug are defined in TagBase

        language = models.CharField(_(u'language'), max_length=10, default='fr')

        person = models.ForeignKey('coop_local.Person', blank=True, null=True, verbose_name=_(u'person'), editable=False)
        person_uri = models.CharField(_(u'person URI'), blank=True, max_length=250, editable=False)
        # category = models.ForeignKey(TagCategory, null=True, blank=True, verbose_name=_(u'category'))

        # Thesaurus link
        concept_uri = models.CharField(_(u'Concept URI'), blank=True, max_length=250, editable=False)

        # Tags have a common uri domain
        domain_name = 'data.economie-solidaire.fr'

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


