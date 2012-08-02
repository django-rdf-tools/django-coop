# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
from django.core.urlresolvers import reverse
from decimal import Decimal
from django.conf import settings
from coop.models import URIModel
from coop.utils.fields import MultiSelectField
import rdflib
from django.contrib.contenttypes import generic

if "coop_geo" in settings.INSTALLED_APPS:
    from coop_geo.models import Area, Location


class BaseProduct(URIModel):
    title = models.CharField(_('title'), blank=True, max_length=250)
    slug = exfields.AutoSlugField(populate_from='title', overwrite=True)
    description = models.TextField(_(u'description'), blank=True)
    organization = models.ForeignKey('coop_local.Organization', blank=True, null=True,
                                        verbose_name='publisher', related_name='products')

    remote_organization_uri = models.CharField(_(u'publisher URI'), blank=True, max_length=200, editable=False)
    remote_organization_label = models.CharField(_('organization'), blank=True, max_length=250)

    def __unicode__(self):
        return self.title + u' (' + self.organization.__unicode__() + u')'

    class Meta:
        abstract = True
        ordering = ['-modified']
        verbose_name = _(u'Product')
        verbose_name_plural = _(u'Products')
        app_label = 'coop_local'


EWAY = Choices(
    ('OFFER',   1,  _(u"I'm offering")),
    ('NEED',    2,  _(u"I'm looking for"))
)

ETYPE = Choices(
    ('PROD',    1,  _(u'Product or Material')),
    ('SERVE',   2,  _(u'Service')),
    ('SKILL',   3,  _(u'Skill')),
    ('COOP',    4,  _(u'Partnership')),
    ('QA',      5,  _(u'Question')),
)


class BaseExchangeMethod(models.Model):  # this model will be initialized with a fixture
    label = models.CharField(_(u'label'), max_length=250)
    uri = models.CharField(_(u'URI'), blank=True, max_length=250)
    etypes = MultiSelectField(_(u'applicable to'), max_length=250, null=True, blank=True, choices=ETYPE.CHOICES)

    def applications(self):
        return u", ".join([ETYPE.CHOICES_DICT[int(e)].__unicode__() for e in self.etypes])
    applications.short_description = _(u'applications')

    def __unicode__(self):
        return self.label

    class Meta:
        abstract = True
        verbose_name = _(u'Exchange method')
        verbose_name_plural = _(u'Exchange methods')
        app_label = 'coop_local'


class BaseExchange(URIModel):
    title = models.CharField(_('title'), max_length=250)
    description = models.TextField(_(u'description'), blank=True)

    organization = models.ForeignKey('coop_local.Organization', blank=True, null=True,
                            verbose_name=_('publisher'), related_name='exchanges')
    person = models.ForeignKey('coop_local.Person', blank=True, null=True, verbose_name=_(u'person'))

    eway = models.PositiveSmallIntegerField(_(u'exchange way'), choices=EWAY.CHOICES, default=EWAY.OFFER)
    etype = models.PositiveSmallIntegerField(_(u'exchange type'), choices=ETYPE.CHOICES)

    permanent = models.BooleanField(_(u'permanent'), default=True)
    expiration = models.DateField(_(u'expiration'), blank=True, null=True)
    slug = exfields.AutoSlugField(populate_from='title', overwrite=True)
    products = models.ManyToManyField('coop_local.Product', verbose_name=_(u'linked products'))

    remote_person_uri = models.CharField(_(u'person URI'), blank=True, max_length=200, editable=False)
    remote_person_label = models.CharField(_('person'), blank=True, max_length=250)

    remote_organization_uri = models.CharField(_(u'organization URI'), blank=True, max_length=200, editable=False)
    remote_organization_label = models.CharField(_('organization'), blank=True, max_length=250)

    methods = models.ManyToManyField('coop_local.ExchangeMethod', verbose_name=_(u'exchange methods'))

    if "coop.agenda" in settings.INSTALLED_APPS:
        dated = generic.GenericRelation('coop_local.Dated')

    # coop_geo must be loaded BEFORE coop_local
    if "coop_geo" in settings.INSTALLED_APPS:

        location = models.ForeignKey(   Location,
                                        verbose_name=_(u'location'),
                                        null=True, blank=True, related_name='exchange_location',
                                        help_text=_("choose a location among your registered locations."))
        area = models.ForeignKey(Area,
                                 verbose_name=_(u'interest area'),
                                 null=True, blank=True, related_name='exchange_area',
                                 help_text=_("choose an area among your registered impact areas."))

    def __unicode__(self):
        return unicode(self.title)

    def get_absolute_url(self):
        return reverse('exchange_detail', args=[self.id])

    def label(self):
        return self.title

    #TODO assign the record to the person editing it (form public) and provide an A-C choice in admin

    class Meta:
        abstract = True
        ordering = ('-modified',)
        verbose_name = _(u'Exchange')
        verbose_name_plural = _(u'Exchanges')
        app_label = 'coop_local'

    # title field needs a special handling. checkDirectMap does not work
    # because two rdf property use the coop_local_organization.title field
    # Thus we have to decide which one to use
    def updateField_title(self, dbfieldname, graph):
            title = list(graph.objects(rdflib.term.URIRef(self.uri), settings.NS.rdfs.label))
            if len(title) == 1:
                self.title = title[0]
                print "For id %s update the field %s" % (self.id, dbfieldname)
            else:
                print "    The field %s cannot be updated." % dbfieldname



class BaseTransaction(models.Model):
    origin = models.ForeignKey('coop_local.Exchange', related_name='origin', verbose_name=_(u'origin'))
    destination = models.ForeignKey('coop_local.Exchange', related_name='destination', verbose_name=_(u'destination'))
    origin_org = models.ForeignKey('coop_local.Organization', related_name='contrats_vente', verbose_name=_(u'vendor'), blank=True, null=True)
    destination_org = models.ForeignKey('coop_local.Organization', related_name='contrats_achat', verbose_name=_(u'buyer'), blank=True, null=True)
    title = models.CharField(_('title'), blank=True, max_length=250)
    description = models.TextField(_(u'description'), blank=True)
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)
    uuid = exfields.UUIDField()  # nécessaire pour URI ?

    def __unicode__(self):
        return self.title

    class Meta:
        abstract = True
        verbose_name = _(u'Transaction')
        verbose_name_plural = _(u'Transactions')
        app_label = 'coop_local'


# MODALITIES = Choices(
#     ('GIFT',    1,  _(u'Gift')),
#     ('TROC',    2,  _(u'Free exchange')),
#     ('CURR',    3,  _(u'Monetary exchange')),
# )
# UNITS = Choices(
#     ('EURO',    1,  _(u'€')),
#     ('SELH',    2,  _(u'Hours')),
#     ('PEZ',     3,  _(u'PEZ')),
# )


# class BasePaymentModality(models.Model):
#     exchange = models.ForeignKey('coop_local.Exchange', verbose_name=_(u'exchange'), related_name='modalities')
#     modality = models.PositiveSmallIntegerField(_(u'exchange type'), blank=True,
#                                                 choices=MODALITIES.CHOICES,
#                                                 default=MODALITIES.CURR)
#     amount = models.DecimalField(_(u'amount'), max_digits=12, decimal_places=2, default=Decimal(0.00), blank=True)
#     unit = models.PositiveSmallIntegerField(_(u'unit'), blank=True, null=True, choices=UNITS.CHOICES)

#     def __unicode__(self):
#         if(self.modality in [1, 2]):
#             return unicode(MODALITIES.CHOICES_DICT[self.modality])
#         elif(self.modality == 3 and self.amount > 0 and not self.unit == None):
#             return unicode("%s %s" % (self.amount, unicode(UNITS.CHOICES_DICT[self.unit])))
#         elif(self.modality == 3):
#             return unicode(_(u'Price unknown'))

#     def save(self, *args, **kwargs):
#         if not self.modality == 3:
#             self.amount = Decimal(0.00)
#             self.unit = None
#         super(BasePaymentModality, self).save(*args, **kwargs)

#     class Meta:
#         abstract = True
#         verbose_name = _(u'Payment modality')
#         verbose_name_plural = _(u'Payment modalities')




