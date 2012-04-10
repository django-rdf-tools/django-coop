# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class BaseMailingList(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)
    email = models.EmailField(_('Newsletter email'))
    main_url = models.URLField(_('List URL'))

    class Meta:
        verbose_name = _('mailing list')
        verbose_name_plural = _('mailing lists')
        abstract = True

    def __unicode__(self):
        return u'%s' % (self.name)


class BaseSubscription(models.Model):
    mailing_list = models.ForeignKey('coop_local.MailingList',
                                        related_name='subs')
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)
    # subscription options (HTML, text ...)
    email = models.EmailField(_('subscribed email'), default='')

    # things which are suscribed
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('mailing list subscription')
        verbose_name_plural = _('mailing list subscriptions')
        abstract = True

    def __unicode__(self):
        return _(u'subscription to ') + unicode(self.mailing_list)
