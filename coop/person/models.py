# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from coop.models import URIModel

if "coop_geo" in settings.INSTALLED_APPS:
    from coop_geo.models import Location


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
    #pour D2RQ et poura voir des URI clean meme pour des non-users

    category = models.ManyToManyField('coop_local.PersonCategory', blank=True, null=True, verbose_name=_(u'category'))
    last_name = models.CharField(_(u'last name'), max_length=100)
    first_name = models.CharField(_(u'first name'), max_length=100, null=True, blank=True)
    contact = generic.GenericRelation('coop_local.Contact')
    email = models.EmailField(_(u'personal email'), blank=True, help_text=_(u'will not be displayed on the website'))
    email_sha1 = models.CharField(_(u'email checksum'), max_length=250, blank=True, null=True)
    notes = models.TextField(_(u'notes'), blank=True, null=True)
    structure = models.CharField(blank=True, max_length=100)

    subs = generic.GenericRelation('coop_local.Subscription')

    if "coop_geo" in settings.INSTALLED_APPS:
        location = models.ForeignKey(Location, null=True, blank=True, verbose_name=_(u'location'))
        location_display = models.PositiveSmallIntegerField(_(u'Display'), choices=DISPLAY.CHOICES, default=DISPLAY.USERS)

    class Meta:
        abstract = True
        verbose_name = _(u'Person')
        verbose_name_plural = _(u'Persons')
        app_label = 'coop_local'

    def __unicode__(self):
        return unicode('%s %s' % (self.first_name, self.last_name))

    @models.permalink
    def get_absolute_url(self):
        return reverse('profiles_profile_detail', args=[self.username])
        #return ('profiles_profile_detail', (), {'username': self.username})

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
        if self.email != '':
            import hashlib
            m = hashlib.sha1()
            m.update(self.email)
            self.email_sha1 = m.hexdigest()

        # create username slug if not set
        if self.username == '':
            newname = slugify(self.first_name).replace('-', '_') + '.' + \
                        slugify(self.last_name).replace('-', '_')
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
        super(BasePerson, self).save(*args, **kwargs)
