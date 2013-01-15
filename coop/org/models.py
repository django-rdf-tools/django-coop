# -*- coding:utf-8 -*-
from django.db import models
from django.db.models import Count
from autoslug import AutoSlugField
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
import rdflib
import coop
from django.contrib.sites.models import Site
import logging
from urlparse import urlsplit


#from mptt.models import MPTTModel, TreeForeignKey
# class BaseClassification(MPTTModel, URIModel):
#     label = models.CharField(_(u'label'), max_length=60)
#     slug = AutoSlugField(populate_from='label', always_update=True, unique=True)
#     parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
#     domain_name = 'thess.economie-solidaire.fr'

#     class MPTTMeta:
#         order_insertion_by = ['label']

#     class Meta:
#         abstract = True
#         verbose_name = _('Classification')
#         verbose_name_plural = _('Classifications')
#         ordering = ['tree_id', 'lft']  # for FeinCMS TreeEditor
#         app_label = 'coop_local'

#     def __unicode__(self):
#         return unicode(self.label)

#     def get_absolute_url(self):
#         return reverse('%s-detail' % self._meta.object_name.lower(), args=[self.slug])

#     @property
#     def uri_id(self):
#         return self.slug

#     def uri_registry(self):
#         return u'label'


class BaseRoleCategory(models.Model):
    label = models.CharField(_(u'label'), max_length=60)
    slug = exfields.AutoSlugField(populate_from=('label'), overwrite=True)
    uri = models.CharField(_(u'URI'), blank=True, max_length=250)

    def save(self, *args, **kwargs):
        self.save_base()
        self.uri = u'http://thess.economie-solidaire.fr/id/role/%s/' % self.slug
        super(BaseRoleCategory, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['label']
        verbose_name = _('Role category')
        verbose_name_plural = _('Role categories')
        #ordering = ['label']
        app_label = 'coop_local'

    def __unicode__(self):
        return unicode(self.label)


class BaseRole(URIModel):
    label = models.CharField(_(u'label'), max_length=120)
    slug = AutoSlugField(populate_from='label', always_update=True, unique=True, editable=False)
    category = models.ForeignKey('coop_local.RoleCategory', null=True, blank=True, verbose_name=_(u'category'))

    domain_name = 'thess.economie-solidaire.fr'

    class Meta:
        abstract = True
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        #ordering = ['tree_id', 'lft']  # for FeinCMS TreeEditor
        #ordering = ['label']
        app_label = 'coop_local'

    @property
    def uri_id(self):
        return self.slug

    def uri_registry(self):
        return u'label'

    def __unicode__(self):
        return unicode(self.label)

    def get_absolute_url(self):
        return reverse('role_detail', args=[self.slug])

    # rdf stuff
    rdf_type = settings.NS.org.Role
    base_mapping = [
        ('single_mapping', (settings.NS.dct.created, 'created'), 'single_reverse'),
        ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
        ('single_mapping', (settings.NS.skos.prefLabel, 'label'), 'single_reverse'),

        # quand RoleCategory sera un URIModels on aura tout simpleùent
        #('single_mapping', (settings.NS.skos.broader, 'category'), 'single_reverse'),

        ('category_mapping', (settings.NS.skos.broader, 'category'), 'category_mapping_reverse'),
    ]

    def category_mapping(self, rdfPred, djF, lang=None):
        value = getattr(self, djF)
        if value == None:
            return []
        else:
            return [(rdflib.term.URIRef(self.uri), rdfPred, rdflib.term.URIRef(value.uri))]

    def category_mapping_reverse(self, g, rdfPred, djF, lang=None):
        values = list(g.objects(rdflib.term.URIRef(self), rdfPred))
        if values == []:
            setattr(self, djF, None)
        elif len(values) == 1:
            value = values[0]
            setattr(self, djF, models.get_model('coop_base', 'rolecategory').object.get(uri=value))


# will apply to contact numbers and other things
# TODO simplify it, see PPO Ontology

DISPLAY = Choices(
    ('PUBLIC',  1,  _(u'public information')),
    ('USERS',   2,  _(u'organiztion members')),
    ('ADMIN',   3,  _(u'administrators of this site')),
)

COMM_MEANS = Choices(
    ('MAIL',    8,  _(u'E-mail')),
    ('LAND',    1,  _(u'Landline phone')),
    ('GSM',     2,  _(u'Mobile phone')),
    ('FAX',     3,  _(u'Fax')),
    ('WEB',     9,  _(u'Secondary web site')),
    ('SKYPE',   4,  _(u'Skype')),
    ('TWITTER', 5,  _(u'Twitter')),
    ('RSS',     6,  _(u'RSS Feed')),
    ('VCAL',    7,  _(u'vCalendar')),
)


class BaseContactMedium(models.Model):  # this model will be initialized with a fixture
    label = models.CharField(_(u'label'), max_length=250)
    uri = models.CharField(_(u'URI'), blank=True, max_length=250)

    def __unicode__(self):
        return self.label

    class Meta:
        abstract = True
        verbose_name = _(u'Contact medium')
        verbose_name_plural = _(u'Contact mediums')
        app_label = 'coop_local'


class BaseContact(URIModel):
    """ A model which represents any communication medium (a phone number, an email) """
    category = models.PositiveSmallIntegerField(_(u'Category'),
                    choices=COMM_MEANS.CHOICES, editable=False, blank=True, null=True)  # TODO erase when data migrated
    contact_medium = models.ForeignKey('coop_local.ContactMedium', blank=True, null=True, verbose_name=u'medium')

    content = models.CharField(_(u'content'), max_length=250)
    details = models.CharField(_(u'details'), blank=True, max_length=100)
    display = models.PositiveSmallIntegerField(_(u'Display'),
                    choices=DISPLAY.CHOICES, default=DISPLAY.PUBLIC)

    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True
        ordering = ['category']
        verbose_name = _(u'Contact')
        verbose_name_plural = _(u'Contacts')
        app_label = 'coop_local'

    def __unicode__(self):
        if self.content_object != None:
            return self.content + u' (' + self.content_object.__unicode__() + u')'
        else:
            return self.content

    def label(self):
        return self.__unicode__()

    @classmethod
    def clean_phone(cls, number):
        import re
        phoneSplitRegex = re.compile(r"[\-\(\) \.\,]")
        parts = phoneSplitRegex.split(number)
        num = ''.join(parts)
        if len(num) == 10:
            cleaned_number = '.'.join((num[:2], num[2:4], num[4:6], num[6:8], num[8:]))
            return cleaned_number
        else:
            raise ValidationError(_(u'Phone numbers must have 10 digits'))

    def save(self, *args, **kwargs):
        if self.category in [1, 2, 3]:
            self.content = self.clean_phone(self.content)
        #logging.error(u'A contact has been created or modified', exc_info=True, extra={'request': request})
        super(BaseContact, self).save(*args, **kwargs)



    # RDF stuff
    def isOpenData(self):
        return self.display == DISPLAY.PUBLIC

    rdf_type = settings.NS.ess.ContactMedium

    base_mapping = [
        ('single_mapping', (settings.NS.dct.created, 'created'), 'single_reverse'),
        ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
        ('single_mapping', (settings.NS.rdf.value, 'content'), 'single_reverse'),
        ('single_mapping', (settings.NS.rdfs.comment, 'details'), 'single_reverse'),

        ('medium_mapping', (settings.NS.rdf.type, 'contact_medium'), 'medium_mapping_reverse'),
    ]


    def medium_mapping(self, rdfPred, djF, lang=None):
        medium = getattr(self, djF)
        rdfSubject = rdflib.URIRef(self.uri)
        return [(rdfSubject, rdfPred, rdflib.URIRef(medium.uri))]


    def medium_mapping_reverse(self, g, rdfPred, djF, lang=None):
        values = list(g.objects(rdflib.term.URIRef(self.uri), rdfPred))        
        values.remove(self.rdf_type)
        m = models.get_model('coop_local', 'contactmedium')
        if len(values) == 1:
            value = values[0]
            medium = m.objects.get(uri=str(value))
            setattr(self, djF, medium)


# TODO : use django-multilingual-ng to translate the label field in multiple languages

class BaseOrgRelationType(models.Model):  # this model will be initialized with a fixture
    label = models.CharField(_(u'label'), max_length=250)
    uri = models.CharField(_(u'URI'), blank=True, max_length=250)
    org_to_org = models.BooleanField(_('available for org-to-org relations'), default=True)
    org_to_project = models.BooleanField(_('available for org-to-project relations'), default=True)

    def __unicode__(self):
        return self.label

    class Meta:
        abstract = True
        verbose_name = _(u'Organizations relation type')
        verbose_name_plural = _(u'Organization relations types')
        app_label = 'coop_local'


RELATIONS = Choices(
    ('MEMBER',          1,  _(u' is member of ')),
    ('REG_SUPPLIER',    2,  _(u' has for regular supplier ')),
    ('OCC_SUPPLIER',    3,  _(u' has for casual supplier ')),
    ('SUPPORT',         4,  _(u' received technical support from ')),
    ('FUNDING',         5,  _(u' received financial support from ')),
)


class BaseRelation(models.Model):
    source = models.ForeignKey('coop_local.Organization', verbose_name=_(u'source organization'), related_name='source')
    target = models.ForeignKey('coop_local.Organization', verbose_name=_(u'target organization'), related_name='target')
    reltype = models.PositiveSmallIntegerField(_(u'Relation type'), choices=RELATIONS.CHOICES, blank=True, null=True)  # TODO erase when data migrated AND remove
    relation_type = models.ForeignKey('coop_local.OrgRelationType',
                                        verbose_name=_(u'relation type'),
                                        null=True, blank=True)

    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)
    #confirmed = models.BooleanField(default=False, verbose_name=_(u'confirmed by the target organization'))

    class Meta:
        abstract = True
        verbose_name = _('Relation')
        verbose_name_plural = _('Relations')
        app_label = 'coop_local'

    def __unicode__(self):
        return _(u"Relation : %(a)s is a %(r)s of %(b)s") % {'a': self.source.__unicode__(),
                                                             'r': self.relation_type.__unicode__(),
                                                             'b': self.target.__unicode__()}
    '''
    # TODO
    def save(self):
        vérifier si la relation inverse existe
    '''


class BaseEngagement(URIModel):
    person = models.ForeignKey('coop_local.Person', verbose_name=_(u'person'), related_name='engagements')
    organization = models.ForeignKey('coop_local.Organization', verbose_name=_(u'organization'))
    role = models.ForeignKey('coop_local.Role', verbose_name=_(u'role'), null=True, blank=True)
    role_detail = models.CharField(_(u'detailed role'), blank=True, max_length=100)
    org_admin = models.BooleanField(_(u'has editor rights'), default=True)
    engagement_display = models.PositiveSmallIntegerField(_(u'Display'), choices=DISPLAY.CHOICES, default=DISPLAY.PUBLIC)

    remote_person_uri = models.URLField(_(u'remote person URI'), blank=True, null=True, max_length=255, editable=False)
    remote_person_label = models.CharField(_(u'remote person label'),
                                                max_length=250, blank=True, null=True,
                                                help_text=_(u'fill this only if the person record is not available locally'))

    remote_role_uri = models.URLField(_(u'URI'), blank=True, null=True, max_length=250)
    remote_role_label = models.CharField(blank=True, null=True, max_length=100)

    remote_organization_uri = models.URLField(_(u'remote organization URI'), blank=True, null=True, max_length=255, editable=False)
    remote_organization_label = models.CharField(_(u'remote organization label'),
                                                max_length=250, blank=True, null=True,
                                                help_text=_(u'fill this only if the organization record is not available locally'))


    class Meta:
        abstract = True
        verbose_name = _('Engagement')
        verbose_name_plural = _('Engagements')
        app_label = 'coop_local'

    def __unicode__(self):
        if self.role:
            return '%(person)s, %(role)s @ %(org)s' % {
                        'person': self.person.__unicode__(),
                        'role': self.role.__unicode__(),
                        'org': self.organization.__unicode__()
                        }
        else:
            return '%(person)s, %(role)s @ %(org)s' % {
                        'person': self.person.__unicode__(),
                        'role': self.remote_role_label if self.remote_role_label else '',
                        'org': self.organization.__unicode__()
                        }

    def label(self):
        return self.__unicode__()

    # RDF stufs
    def isOpenData(self):
        return self.engagement_display == DISPLAY.PUBLIC

    rdf_type = settings.NS.org.Membership
    base_mapping = [
        ('single_mapping', (settings.NS.dct.created, 'created'), 'single_reverse'),
        ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
        ('single_mapping', (settings.NS.org.member, 'person'), 'single_reverse'),

        ('local_or_remote_mapping', (settings.NS.org.organization, 'organization'), 'local_or_remote_reverse'),
        ('local_or_remote_mapping', (settings.NS.org.role, 'role'), 'local_or_remote_reverse'),

        ('label_mapping', (settings.NS.rdfs.label, 'id', 'fr'), 'label_mapping_reverse'),

    ]

    def label_mapping(self, rdfPred, djF, lang):
        return [(rdflib.term.URIRef(self.uri), rdfPred, rdflib.term.Literal(u'Engagement n°%s' % self.id, lang))]

    def label_mapping_reverse(self, g, rdfPred, djF, lang=None):
        pass


class BaseOrganizationCategory(models.Model):
    label = models.CharField(blank=True, max_length=100)
    slug = exfields.AutoSlugField(populate_from=('label'), overwrite=True)
    description = models.TextField(_(u'description'), blank=True)

    class Meta:
        abstract = True
        verbose_name = _(u'organization category')
        verbose_name_plural = _(u'organization categories')
        app_label = 'coop_local'

    def __unicode__(self):
        return self.label

    #@models.permalink
    def get_absolute_url(self):
        return reverse('org_category_detail', args=[self.slug])

    def get_edit_url(self):
        return reverse('org_category_edit', args=[self.slug])

    def get_cancel_url(self):
        return reverse('org_category_edit_cancel', args=[self.slug])

    def _can_modify_organizationcategory(self, user):
        if user.is_authenticated():
            if user.is_superuser:
                return True
            else:
                return False

    def can_view_organizationcategory(self, user):
        # TODO use global privacy permissions on objects
        return True

    def can_edit_organizationcategory(self, user):
        return self._can_modify_organizationcategory(user)







PREFLABEL = Choices(
    ('TITLE',   1,  _(u'title')),
    ('ACRO',    2,  _(u'acronym')),
)


def get_logo_folder(self, filename):
    img_root = 'org_logos'
    return u'{0}/{1}/{2}'.format(img_root, self.id, filename)


class BaseOrganization(URIModel):
    title = models.CharField(_(u'title'), max_length=250)

    acronym = models.CharField(_(u'acronym'), max_length=100, blank=True, null=True)
    pref_label = models.PositiveSmallIntegerField(_(u'Preferred label'),
                        choices=PREFLABEL.CHOICES, default=PREFLABEL.TITLE)

    subtitle = models.CharField(_(u'tagline'), blank=True, null=True,
                max_length=250,
                help_text=_(u'tell us what your organization do in one line.'))

    description = models.TextField(_(u'description'), blank=True, null=True)

    logo = ImageField(upload_to='logos/', null=True, blank=True)
    #temp_logo = models.ImageField(upload_to=get_logo_folder, blank=True, null=True, default='')


    relations = models.ManyToManyField('coop_local.Organization',
                symmetrical=False, through='coop_local.Relation',
                verbose_name=_(u'relations'))

    category = models.ManyToManyField('coop_local.OrganizationCategory',
                blank=True, null=True, verbose_name=_(u'category'))

    members = models.ManyToManyField('coop_local.Person',
                through='coop_local.Engagement', verbose_name=_(u'members'))

    contacts = generic.GenericRelation('coop_local.Contact')

    if 'coop.mailing' in settings.INSTALLED_APPS:
        subs = generic.GenericRelation('coop_local.Subscription')

    # ORDER : coop_geo must be loaded BEFORE coop_local
    if "coop_geo" in settings.INSTALLED_APPS:
        located = generic.GenericRelation('coop_geo.Located')  # , related_name='located_org')
        framed = generic.GenericRelation('coop_geo.AreaLink')  # , related_name='framed_org')

    birth = models.DateField(_(u'creation date'), null=True, blank=True)
    email = models.EmailField(_(u'global email'), blank=True, null=True)
    email_sha1 = models.CharField(_(u'email checksum'),
            max_length=250, blank=True, null=True)  # TODO : do this in Postgre
    web = models.URLField(_(u'web site'), blank=True, null=True)

    pref_email = models.ForeignKey('coop_local.Contact',
                verbose_name=_(u'preferred email'),
                related_name="pref_email", null=True, blank=True)
    pref_phone = models.ForeignKey('coop_local.Contact',
                verbose_name=_(u'preferred phone'),
                related_name='pref_phone', null=True, blank=True)
    pref_address = models.ForeignKey('coop_local.Location',
                verbose_name=_(u'preferred postal address'),
                related_name='pref_adress', null=True, blank=True)

    slug = exfields.AutoSlugField(populate_from='title', blank=True, overwrite=True)
    active = models.BooleanField(_(u'show on public site'), default=True,)
    notes = models.TextField(_(u'notes'), blank=True)

    if "coop.agenda" in settings.INSTALLED_APPS:
        dated = generic.GenericRelation('coop_local.Dated')

    class Meta:
        abstract = True
        ordering = ['title']
        verbose_name = _(u'Organization')
        verbose_name_plural = _(u'Organizations')
        app_label = 'coop_local'

    def __unicode__(self):
        return unicode(self.title)

    def label(self):
        if self.pref_label == PREFLABEL.TITLE:
            return self.title
        elif self.pref_label == PREFLABEL.ACRO:
            return self.acronym

    if "coop_geo" in settings.INSTALLED_APPS:

        def has_location(self):
            return self.located.all().count() > 0
        has_location.boolean = True
        has_location.short_description = _(u'geo')

        def locations(self):
            from coop_local.models import Location
            return Location.objects.filter(id__in=self.located.all().values_list('location_id', flat=True))

        def areas(self):
            from coop_local.models import Area
            return Area.objects.filter(id__in=self.framed.all().values_list('location_id', flat=True))

        def to_geoJson(self):
            if self.pref_address and self.pref_address.point:
                return {
                   "type": "Feature",
                    "properties": {
                            "name": self.label(),
                            "popupContent": u"<h4>" + self.label() + u"</h4><p><a href='" + \
                            self.get_absolute_url() + u"'>" + self.label() + u"</a></p>"
                            },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [self.pref_address.point.x, self.pref_address.point.y]
                            }
                        }

    def has_description(self):
        return self.description != None and len(self.description) > 20
    has_description.boolean = True
    has_description.short_description = _(u'desc.')
    

    def logo_list_display(self):
        try:
            if self.logo:
                thumb = default.backend.get_thumbnail(self.logo.file, settings.ADMIN_THUMBS_SIZE)
                return '<img width="%s" src="%s" />' % (thumb.width, thumb.url)
            else:
                return _(u"No Image")
        except IOError:
            return _(u"No Image")

    logo_list_display.short_description = _(u"logo")
    logo_list_display.allow_tags = True

    #@models.permalink
    def get_absolute_url(self):
        return reverse('org_detail', args=[self.slug])

    def get_relations(self):
        relations = {}
        relmap = RELATIONS.REVERTED_CHOICES_CONST_DICT

        for rel in self.source.all():
            reltype = str('OUT_' + relmap[rel.reltype])  # me => others
            relations[reltype] = []
            relations[reltype].append(rel.target)
        for rel in self.target.all():
            reltype = str('IN_' + relmap[rel.reltype])  # others said this
            if reltype not in relations:
                relations[reltype] = []
            #if rel.confirmed:  # which one are confirmed by both parts
            relations[reltype].append(rel.source)
        return relations

    # def local_uri(self):
    #     return ('http://dev.credis.org:8000/org/' + self.slug + '/')

    def main_location(self):
        if self.located.all().exists():
            return self.located.all()[0].location
        else:
            return None

    def save(self, *args, **kwargs):
        # Set default values for preferred email, phone and postal address
        if self.pref_phone == None:
            phone_categories = [1, 2]
            fixes = self.contacts.filter(category__in=phone_categories)
            if fixes.count() == 1:
                self.pref_phone = fixes[0]
        if self.pref_email == None:
            orgmails = self.contacts.filter(category=8)
            if orgmails.count() > 0:
                self.pref_email = orgmails[0]
        if 'coop_geo' in settings.INSTALLED_APPS:
            if self.pref_address == None:
                locations = self.located.all()  # should we have a "main venue" ?
                if locations.count() > 0:
                    self.pref_address = locations[0].location

        # TODO move this to Contact model or do it in SQL

        # if self.email and self.email != '':
        #     import hashlib
        #     m = hashlib.sha1()
        #     m.update(self.email)
        #     self.email_sha1 = m.hexdigest()
        super(BaseOrganization, self).save(*args, **kwargs)

    def get_edit_url(self):
        return reverse('org_edit', args=[self.slug])

    def get_cancel_url(self):
        return reverse('org_edit_cancel', args=[self.slug])

    def _can_modify_organization(self, user):
        if user.is_authenticated():
            if user.is_superuser:
                return True
            elif user.person in self.members.all():
                return True
            else:
                return False

    def can_view_organization(self, user):
        # TODO use global privacy permissions on objects
        return True

    def can_edit_organization(self, user):
        return self._can_modify_organization(user)

    rdf_type = settings.NS.org.Organization

    def isOpenData(self):
        return self.active

    base_mapping = [
        ('single_mapping', (settings.NS.dct.created, 'birth'), 'single_reverse'),
        ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
        ('single_mapping', (settings.NS.legal.legalName, 'title'), 'single_reverse'),
        ('single_mapping', (settings.NS.ov.prefAcronym, 'acronym'), 'single_reverse'),
        ('single_mapping', (settings.NS.rdfs.comment, 'subtitle'), 'single_reverse'),
        ('single_mapping', (settings.NS.dct.description, 'description'), 'single_reverse'),
        ('single_mapping', (settings.NS.foaf.mbox_sha1sum, 'email_sha1'), 'single_reverse'),
        ('single_mapping', (settings.NS.foaf.homepage, 'web'), 'single_reverse'),
        ('single_mapping', (settings.NS.foaf.birthday, 'birth'), 'single_reverse'),
        ('single_mapping', (settings.NS.vcard.tel, 'pref_phone'), 'single_reverse'),
        ('single_mapping', (settings.NS.vcard.mail, 'pref_email'), 'single_reverse'),
        ('single_mapping', (settings.NS.legal.registeredAddress, 'pref_address'), 'single_reverse'),
        ('single_mapping', (settings.NS.skos.note, 'notes'), 'single_reverse'),

        ('multi_mapping', (settings.NS.dct.subject, 'tags'), 'multi_reverse'), 
        # FIXME : Organization objects need to have a primary key value before you can access their tags.

        ('multi_mapping', (settings.NS.ess.hasContactMedium, 'contacts'), 'multi_reverse'),
        # FIXME : 'Contact' instance expected

        ('multi_mapping', (settings.NS.org.hasMember, 'members'), 'none_reverse'),
        # FIXME : 'Organization' instance needs to have a primary key value before a many-to-many relationship can be used.


        ('logo_mapping', (settings.NS.foaf.logo, 'logo'), 'logo_mapping_reverse'),
        ('prefLabel_mapping', (settings.NS.rdfs.label, 'pref_label'), 'prefLabel_mapping_reverse'),
    
        ('location_mapping', (settings.NS.locn.location, 'located'), 'location_mapping_reverse'),
        # FIXME : Located matching query does not exist.

        ('location_mapping', (settings.NS.ess.actionArea, 'framed'), 'location_mapping_reverse'),
        ('exchange_mapping', (settings.NS.gr.offers, settings.NS.gr.seeks), 'exchange_mapping_reverse'),
        ('engagement_mapping', (settings.NS.org.organization, 'engagement_set'), 'engagement_mapping_reverse'),

    ]


    # We to add in the graph the coresponding Engagement
    def engagement_mapping(self, rdfPred, djF):
        res = []
        for e in getattr(self, djF).all():
            res.append((rdflib.term.URIRef(e.uri), rdfPred, rdflib.term.URIRef(self.uri)))
        return res

    def engagement_mapping_reverse(self, g, rdfPred, djF):
        pass

    def location_mapping(self, rdfPred, djF):
        values = map(lambda x: x.location, getattr(self, djF).all())
        return self.multi_mapping_base(values, rdfPred)

    def location_mapping_reverse(self, g, rdfPred, djField, lang=None):
        rdf_values = set(g.objects(rdflib.term.URIRef(self.uri), rdfPred))
        # Values contient des instances de Location. 
        # Il faut remonter soit a des Located soit a des AreaLink
        values = map(coop.models.StaticURIModel.toDjango, rdf_values)
        if djField == 'located':
            m = models.get_model('coop_geo', 'located')
            try:
                values = set(map(lambda x: m.objects.get(object_id=self.id, location=x), values))
            except m.DoesNotExist:
                values = set([])
        elif djField == 'framed':
            m = models.get_model('coop_geo', 'arealink')
            try:
                values = set(map(lambda x: m.objects.get(object_id=self.id, location=x), values))
            except m.DoesNotExist:
                values = set([])
        manager = getattr(self, djField)
        old_values = set(manager.all())
        remove = old_values.difference(values)
        add = values.difference(old_values)
        for v in remove:
            manager.remove(v)
        for v in add:
            manager.add(v)

    def logo_mapping(self, rdfPred, djF):
        logo = getattr(self, djF)
        if logo == None:
            return []
        else:
            try:
                rdfSubject = rdflib.term.URIRef(self.uri)
                rdfValue = rdflib.term.URIRef('http://' + str(Site.objects.get_current().domain) + logo.url)
                return [(rdfSubject, rdfPred, rdfValue)]
            except ValueError:
                return []

    # TODO : télécharger le logo dans un dossier /tmp et le passer à sorl.thumbnail pour traitement
    def logo_mapping_reverse(self, g, rdfPred, djF):
        value = list(g.objects(rdflib.term.URIRef(self.uri), rdfPred))
        if len(value) == 1:
            value = value[0].toPython()
            scheme, host, path, query, fragment = urlsplit(value)
            sp = path.split('/')
            setattr(self, djF, "%s:%s" % (sp[len(sp) - 2], sp[len(sp) - 1]))
        else:
            pass

    def prefLabel_mapping(self, rdfPred, djF, lang=None):
        label = self.label()
        if label == None:
            return []
        else:
            subject_args = {}
            if lang:
                subject_args['lang'] = lang
            rdfValue = rdflib.term.Literal(unicode(label), **subject_args)
            return[(rdflib.term.URIRef(self.uri), rdfPred, rdfValue)]

    def prefLabel_mapping_reverse(self, g, rdfPred, djF, lang=None):
        value = list(g.objects(rdflib.term.URIRef(self.uri), rdfPred))
        title = list(g.objects(rdflib.term.URIRef(self.uri), settings.NS.legal.legalName))
        if value == title:
            setattr(self, 'pref_label', PREFLABEL.TITLE)
        else:
            setattr(self, 'pref_label', PREFLABEL.ACRO)

    def exchange_mapping(self, rdfOffer, rdfSeek, lang=None):
        from coop.exchange.models import EWAY
        values = models.get_model('coop_local', 'exchange').objects.filter(organization=self)
        rdfSubject = rdflib.term.URIRef(self.uri)
        result = []
        for value in values:
            if value.eway == EWAY.OFFER:
                result.append((rdfSubject, rdfOffer, rdflib.term.URIRef(value.uri)))
            else:
                result.append((rdfSubject, rdfSeek, rdflib.term.URIRef(value.uri)))
        return result

    def exchange_mapping_reverse(self, g, rdfOffer, rdfSeek, lang=None):
        from coop.exchange.models import EWAY
        values = list(g.objects(rdflib.term.URIRef(self.uri), rdfOffer))
        exchangeModel = models.get_model('coop_local', 'exchange')
        for value in values:
            exists = exchangeModel.objects.filter(uri=str(value)).exists()
            if exists:
                ex = exchangeModel.objects.get(uri=str(value))
                ex.eway = EWAY.OFFER
                ex.organization = self
                ex.save()
        values = list(g.objects(rdflib.term.URIRef(self.uri), rdfSeek))
        for value in values:
            exists = exchangeModel.objects.filter(uri=str(value)).exists()
            if exists:
                ex = exchangeModel.objects.get(uri=str(value))
                ex.eway = EWAY.NEED
                ex.organization = self
                ex.save()


# TODO : use django-multilingual-ng to translate the label field in multiple languages
# Copied from OrgrelationType, goal is to use the same properties, as Project are Collaborations, a RDF subclass of project

# class BaseCollaborationType(models.Model):  # this model will be initialized with a fixture
#     label = models.CharField(_(u'label'), max_length=250)
#     uri = models.CharField(_(u'URI'), blank=True, max_length=250)

#     def __unicode__(self):
#         return self.label

#     class Meta:
#         verbose_name = _(u'Collaboration type')
#         verbose_name_plural = _(u'Collaboration types')
#         app_label = 'coop_local'




