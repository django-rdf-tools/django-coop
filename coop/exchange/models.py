# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
from django.core.urlresolvers import reverse
from decimal import Decimal
from django.conf import settings
from coop.models import URIModel

if "coop_geo" in settings.INSTALLED_APPS:
    from coop_geo.models import Area, Location


MODALITIES = Choices(
    ('GIFT',    1,  _(u'Gift')),
    ('TROC',    2,  _(u'Free exchange')),
    ('CURR',    3,  _(u'Monetary exchange')),
)
UNITS = Choices(
    ('EURO',    1,  _(u'€')),
    ('SELH',    2,  _(u'Hours')),
    ('PEZ',     3,  _(u'PEZ')),    
)


class BasePaymentModality(models.Model):
    exchange = models.ForeignKey('coop_local.Exchange', verbose_name=_(u'exchange'), related_name='modalities')
    modality = models.PositiveSmallIntegerField(_(u'exchange type'), blank=True,
                                                choices=MODALITIES.CHOICES,
                                                default=MODALITIES.CURR)
    amount = models.DecimalField(_(u'amount'), max_digits=12, decimal_places=2, default=Decimal(0.00), blank=True)
    unit = models.PositiveSmallIntegerField(_(u'unit'), blank=True, null=True, choices=UNITS.CHOICES)

    def __unicode__(self):
        if(self.modality in [1, 2]):
            return unicode(MODALITIES.CHOICES_DICT[self.modality])
        elif(self.modality == 3 and self.amount > 0 and not self.unit == None):
            return unicode("%s %s" % (self.amount, unicode(UNITS.CHOICES_DICT[self.unit])))
        elif(self.modality == 3):
            return unicode(_(u'Price unknown'))

    def save(self, *args, **kwargs):
        if not self.modality == 3:
            self.amount = Decimal(0.00)
            self.unit = None
        super(BasePaymentModality, self).save(*args, **kwargs) 

    class Meta:
        abstract = True
        verbose_name = _(u'Payment modality')
        verbose_name_plural = _(u'Payment modalities')


class BaseProduct(URIModel):
    title = models.CharField(_('title'), blank=True, max_length=250)
    slug = exfields.AutoSlugField(populate_from='title')
    description = models.TextField(_(u'description'), blank=True)
    organization = models.ForeignKey('coop_local.Organization', blank=True, null=True, 
                                        verbose_name='publisher', related_name='products')
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)
    uri = models.CharField(_(u'main URI'), blank=True, max_length=250, editable=False)
    publisher_uri = models.CharField(_(u'publisher URI'), blank=True, max_length=200, editable=False)

    @property
    def uri_id(self):
        return self.id
    uri_fragment = 'product'

    def __unicode__(self):
        return self.title

    class Meta:
        abstract = True
        verbose_name = _(u'Product')
        verbose_name_plural = _(u'Products')


EXCHANGE = Choices(
    ('P_OFFER',   1,  _(u'Product Offer')),
    ('S_OFFER',   2,  _(u'Service Offer')),
    ('P_NEED',    3,  _(u'Product Need')),
    ('S_NEED',    4,  _(u'Service Need')),
    ('MUTU',    7,  _(u'Mutualization')),
    ('COOP',    8,  _(u'Cooperation, partnership')),
    ('QA',      9,  _(u'Question')),
)

EWAY = Choices(
    ('OFFER',   1,  _(u"I'm offering")),
    ('NEED',    2,  _(u"I'm looking for"))
)

ETYPE = Choices(
    ('PROD',    1,  _(u'Product')),
    ('SERVE',   2,  _(u'Service')),
    ('SKILL',   3,  _(u'Skill')),
    ('COOP',    4,  _(u'Partnership')),
    ('QA',      5,  _(u'Question')),
)


class BaseExchange(URIModel):
    title = models.CharField(_('title'), max_length=250)
    description = models.TextField(_(u'description'), blank=True)
    organization = models.ForeignKey('coop_local.Organization', blank=True, null=True, 
                            verbose_name=_('publisher'), related_name='exchanges')
    person = models.ForeignKey('coop_local.Person', blank=True, null=True, verbose_name=_(u'person'))
    
    eway = models.PositiveSmallIntegerField(' ', choices=EWAY.CHOICES, default=EWAY.OFFER)  # verbose name void on purpose !
    etype = models.PositiveSmallIntegerField(_(u'exchange type'), choices=ETYPE.CHOICES)

    permanent = models.BooleanField(_(u'permanent'), default=True)
    expiration = models.DateField(_(u'expiration'), blank=True, null=True)
    slug = exfields.AutoSlugField(populate_from='title')
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)
    products = models.ManyToManyField('coop_local.Product', verbose_name=_('linked products'))
    uri = models.CharField(_(u'main URI'), blank=True, max_length=250, editable=False)
    author_uri = models.CharField(_(u'author URI'), blank=True, max_length=200, editable=False)
    publisher_uri = models.CharField(_(u'publisher URI'), blank=True, max_length=200, editable=False)

    mod_euro = models.BooleanField(_(u'Euros'), default=False)
    mod_free = models.BooleanField(_(u'Gift'), default=False)
    mod_troc = models.BooleanField(_(u'Barter'), default=False)
    mod_mutu = models.BooleanField(_(u'Mutualization'), default=False)
    mod_mc = models.BooleanField(_(u'Alternative currency'), default=False)

    mod_job = models.BooleanField(_(u'Job'), default=False)
    mod_stage = models.BooleanField(_(u'Training'), default=False)
    mod_benevolat = models.BooleanField(_(u'Voluntary'), default=False)
    mod_volontariat = models.BooleanField(_(u'Civic work'), default=False)



    uuid = exfields.UUIDField()  # nécessaire pour URI ?
    # coop_geo must be loaded BEFORE coop_local
    if "coop_geo" in settings.INSTALLED_APPS:
        location = models.ForeignKey(Location, null=True, blank=True, verbose_name=_(u'location'))
        area = models.ForeignKey(Area, null=True, blank=True, verbose_name=_(u'area'))    

    def __unicode__(self):
        return unicode(self.title)

    def get_absolute_url(self):
        return reverse('annonce_detail', args=[self.uuid])

    #TODO assign the record to the person editing it (form public) and provide an A-C choice in admin

    @property
    def uri_id(self):
        return self.uuid
    uri_fragment = 'exchange'

    class Meta:
        abstract = True
        verbose_name = _(u'Exchange')
        verbose_name_plural = _(u'Exchanges')


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
