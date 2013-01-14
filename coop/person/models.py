# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.template.defaultfilters import slugify
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from coop.models import URIModel
import rdflib

# if "coop_geo" in settings.INSTALLED_APPS:
#     from coop_local.models import Location


class BasePersonCategory(models.Model):
    label = models.CharField(blank=True, max_length=100)
    slug = exfields.AutoSlugField(populate_from=('label'), overwrite=True)

    class Meta:
        abstract = True
        verbose_name = _(u'Person category')
        verbose_name_plural = _(u'Person categories')
        app_label = 'coop_local'

    def __unicode__(self):
        return self.label

from coop.org.models import DISPLAY


class BasePerson(URIModel):
    user = models.OneToOneField(User, blank=True, null=True, unique=True, verbose_name=_(u'django user'), editable=False)
    username = models.CharField(blank=True, max_length=100, unique=True)
    category = models.ManyToManyField('coop_local.PersonCategory', blank=True, null=True, verbose_name=_(u'category'))
    last_name = models.CharField(_(u'last name'), max_length=100)
    first_name = models.CharField(_(u'first name'), max_length=100, null=True, blank=True)
    contacts = generic.GenericRelation('coop_local.Contact')
    email = models.EmailField(_(u'personal email'), blank=True)
    notes = models.TextField(_(u'notes'), blank=True, null=True)

    pref_email = models.ForeignKey('coop_local.Contact',
                verbose_name=_(u'preferred email'),
                related_name="preferred_email", null=True, blank=True,
                help_text=_(u'will not be displayed on the website'))

    structure = models.CharField(blank=True, max_length=100)


    if 'coop.mailing' in settings.INSTALLED_APPS:
        subs = generic.GenericRelation('coop_local.Subscription')

    if "coop_geo" in settings.INSTALLED_APPS:
        location = models.ForeignKey('coop_local.Location', null=True, blank=True, verbose_name=_(u'location'))
        location_display = models.PositiveSmallIntegerField(_(u'Display'), choices=DISPLAY.CHOICES, default=DISPLAY.USERS)

    class Meta:
        abstract = True
        verbose_name = _(u'Person')
        verbose_name_plural = _(u'Persons')
        app_label = 'coop_local'

    def __unicode__(self):
        return unicode('%s %s' % (self.first_name, self.last_name))

    #@models.permalink
    def get_absolute_url(self):
        return reverse_lazy('coop.person.views.public_profile', kwargs={'uuid': self.uuid})

    def has_user_account(self):
        return (self.user != None)
    has_user_account.boolean = True
    has_user_account.short_description = _(u'django account')

    def has_role(self):
        return (self.engagements.count() > 0)
    has_role.boolean = True
    has_role.short_description = _(u'has organization')

    def label(self):
        return self.__unicode__()

    def engagements(self):
        eng = []
        for e in self.engagement_set.all():
            eng.append({'initiative': e.initiative, 'role': e.role})
        return eng

    def save(self, *args, **kwargs):
        # if self.email != '':
        #     import hashlib
        #     m = hashlib.sha1()
        #     m.update(self.email)
        #     self.email_sha1 = m.hexdigest()

        # create username slug if not set
        if self.username == '':
            from coop_local.models import Person
            newname = slugify(self.first_name).replace('-', '_') + '.' + \
                        slugify(self.last_name).replace('-', '_')
            if Person.objects.filter(username=newname).exists():
                offset = Person.objects.filter(username=newname).count()
                newname = newname + '_' + str(offset + 1)
            self.username = newname

        # synchronize fields with django User model
        if self.user:
            chg = False
            for field in ('username', 'first_name', 'last_name', 'email'):
                if(getattr(self.user, field) != getattr(self, field)):
                    setattr(self.user, field, getattr(self, field))
                    chg = True
            if(chg):
                self.user.save()

        if self.pref_email == None:
            emails = self.contacts.filter(category=8)
            if emails.count() > 0:
                self.pref_email = emails[0]

        super(BasePerson, self).save(*args, **kwargs)


    # RDF stuf
    rdf_type = settings.NS.person.Person
    base_mapping = [
        ('single_mapping', (settings.NS.dct.created, 'created'), 'single_reverse'),
        ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
        ('single_mapping', (settings.NS.foaf.familyName, 'last_name'), 'single_reverse'),
        ('single_mapping', (settings.NS.foaf.givenName, 'first_name'), 'single_reverse'),
        #('single_mapping', (settings.NS.foaf.mbox_sha1sum, 'email_sha1'), 'single_reverse'),
        ('single_mapping', (settings.NS.skos.note, 'notes'), 'single_reverse'),
 
        ('multi_mapping', (settings.NS.dct.subject, 'tags'), 'multi_reverse'),
        # TODO Person objects need to have a primary key value before you can access their tags.

        ('multi_mapping', (settings.NS.ess.hasContactMedium, 'contact'), 'multi_reverse'),

        ('name_mapping', (settings.NS.foaf.name, 'username'), 'name_mapping_reverse'),
        ('name_mapping', (settings.NS.rdfs.label, 'username'), 'name_mapping_reverse'),
        ('location_mapping', (settings.NS.locn.location, 'location'), 'location_mapping_reverse'),
        ('engagement_mapping', (settings.NS.org.member, 'engagements'), 'engagement_mapping_reverse'),

    ]


    # We to add in the graph the coresponding Engagement
    def engagement_mapping(self, rdfPred, djF):
        res = []
        for e in getattr(self, djF).all():
            res.append((rdflib.URIRef(e.uri), rdfPred, rdflib.URIRef(self.uri)))
        return res

    def engagement_mapping_reverse(self, g, rdfPred, djF):
        pass


    def name_mapping(self, rdfPred, djF, lang=None):
        if (self.first_name == "" or self.first_name == None) and self.last_name == "":
            return [(rdflib.term.URIRef(self.uri), rdfPred, rdflib.term.Literal(self.username, lang))]
        else:
            return [(rdflib.term.URIRef(self.uri), rdfPred, rdflib.term.Literal(u"%s %s" % (self.first_name, self.last_name), lang))]

    def name_mapping_reverse(self, g, rdfP, djF, lang=None):
        pass

    def location_mapping(self, rdfPred, djF, lang=None):
        if hasattr(self, 'location_display') and self.location_display == DISPLAY.PUBLIC:
            if self.location:
                return[(rdflib.term.URIRef(self.uri), rdfPred, rdflib.term.URIRef(self.location.uri))]
        return []

    def location_mapping_reverse(self, g, rdfP, djF, lang=None):
        pass
