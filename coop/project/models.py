# -*- coding:utf-8 -*-
from django.db import models
from extended_choices import Choices
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.conf import settings
from coop.models import URIModel
from sorl.thumbnail import ImageField
from sorl.thumbnail import default
from django.contrib.sites.models import Site
import logging
from urlparse import urlsplit
from coop.org.models import DISPLAY
import rdflib

class BaseProjectCategory(models.Model):
    label = models.CharField(blank=True, max_length=100)
    slug = exfields.AutoSlugField(populate_from=('label'), overwrite=True)
    description = models.TextField(_(u'description'), blank=True)

    class Meta:
        abstract = True
        verbose_name = _(u'project category')
        verbose_name_plural = _(u'project categories')
        app_label = 'coop_local'

    def __unicode__(self):
        return self.label

    #@models.permalink
    # def get_absolute_url(self):
    #     return reverse('org_category_detail', args=[self.slug])

    # def get_edit_url(self):
    #     return reverse('org_category_edit', args=[self.slug])

    # def get_cancel_url(self):
    #     return reverse('org_category_edit_cancel', args=[self.slug])

    # def _can_modify_organizationcategory(self, user):
    #     if user.is_authenticated():
    #         if user.is_superuser:
    #             return True
    #         else:
    #             return False

    # def can_view_organizationcategory(self, user):
    #     # TODO use global privacy permissions on objects
    #     return True

    # def can_edit_organizationcategory(self, user):
    #     return self._can_modify_organizationcategory(user)




PROJECT_STATUS = (
    (1,  _(u'just thinking about it')),  # u'en réflexion'),
    (2,  _(u'looking for partners')),  # u'en recherche de partenariat'),
    (3,  _(u'preparing launch')),  # en cours de montage'),
    (4,  _(u'currently running')),  # u'en cours de réalisation'),
    (5,  _(u'acheived')),  # u'terminé')
)


class BaseProjectMember(URIModel):
    person = models.ForeignKey('coop_local.Person', verbose_name=_(u'person'), related_name='project_members')
    project = models.ForeignKey('coop_local.Project', verbose_name=_(u'project'))
    role_detail = models.CharField(_(u'detailed role'), blank=True, max_length=100)
    is_contact = models.BooleanField(_(u'is contact'), default=True)
    membership_display = models.PositiveSmallIntegerField(_(u'Display'), choices=DISPLAY.CHOICES, default=DISPLAY.PUBLIC)

    class Meta:
        abstract = True
        verbose_name = _('Project member')
        verbose_name_plural = _('Project members')
        app_label = 'coop_local'

    def __unicode__(self):
        return '%(person)s, %(role_detail)s for project %(project)s' % {
                        'person': self.person.__unicode__(),
                        'role_detail': self.role_detail,
                        'project': self.project.__unicode__()
                        }

    def label(self):
        return self.__unicode__()

    # RDF stufs
    def isOpenData(self):
        return self.membership_display == DISPLAY.PUBLIC

    rdf_type = settings.NS.org.Membership  # OK marche aussi pour Project
    base_mapping = [
        ('single_mapping', (settings.NS.dct.created, 'created'), 'single_reverse'),
        ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
        ('single_mapping', (settings.NS.org.member, 'person'), 'single_reverse'),

        ('single_mapping', (settings.NS.org.organization, 'organization'), 'single_reverse'),
        ('single_mapping', (settings.NS.skos.note, 'role_detail'), 'single_reverse'),

        ('label_mapping', (settings.NS.rdfs.label, 'id', 'fr'), 'label_mapping_reverse'),
    ]

    def label_mapping(self, rdfPred, djF, lang):
        return [(rdflib.term.URIRef(self.uri), rdfPred, rdflib.term.Literal(u'Project member n°%s' % self.id, lang))]

    def label_mapping_reverse(self, g, rdfPred, djF, lang=None):
        pass


class BaseProject(URIModel):
    title = models.CharField(_(u'Title'), max_length=250)
    slug = exfields.AutoSlugField(populate_from='title', blank=True, overwrite=True)
    organization = models.ForeignKey('coop_local.Organization', verbose_name=_("organization"), related_name="project_organizer")
    status = models.PositiveSmallIntegerField(_(u"status"), choices=PROJECT_STATUS)
    start = models.DateField(_(u'start date'), blank=True, null=True)
    end = models.DateField(_(u'end date'), blank=True, null=True)
    description = models.TextField(_(u'Description'))
    notes = models.TextField(_(u'notes'), blank=True, null=True)
    published = models.BooleanField(_(u'published on the web site'), default=False)

    zone = models.ForeignKey('coop_local.Area', verbose_name=_(u"zone"), null=True, blank=True)
    budget = models.PositiveIntegerField(_(u'budget'), blank=True, null=True)
    relations = models.ManyToManyField('coop_local.Organization',
                through='coop_local.ProjectSupport',
                verbose_name=_(u'project partners'), related_name='support')
    category = models.ManyToManyField('coop_local.ProjectCategory',
                blank=True, null=True, verbose_name=_(u'category'))

    class Meta:
        verbose_name = _(u"Project")
        verbose_name_plural = _(u"Projects")
        app_label = 'coop_local'
        abstract = True

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', args=[self.id])

    # TODO mapper sur org:OrganizationalCollaboration (alternative name : org:Project)


class BaseProjectSupport(models.Model):
    project = models.ForeignKey('coop_local.Project', verbose_name=_(u'project'), related_name='project')
    partner = models.ForeignKey('coop_local.Organization', verbose_name=_(u'partner'), related_name='partner')
    relation_type = models.ForeignKey('coop_local.OrgRelationType', verbose_name=_(u'relation type'))

    class Meta:
        verbose_name = _(u'Collaboration')
        verbose_name_plural = _(u'Collaborations')
        app_label = 'coop_local'
        abstract = True

    def __unicode__(self):
        return _(u" %(a)s is %(b)s for the project %(p)s ") % {'a': self.partner.__unicode__(),
                                                              'b': self.relation_type.__unicode__(),
                                                              'p': self.project.__unicode__()}


    # TODO mapper sur org:linkedTO


