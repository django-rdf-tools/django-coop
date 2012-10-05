# -*- coding:utf-8 -*-

from django.db import models
from preferences.models import Preferences
from django.utils.translation import ugettext_lazy as _


class BaseSitePrefs(Preferences):
    __module__ = 'preferences.models'
    main_organization = models.ForeignKey('coop_local.Organization', null=True, blank=True, verbose_name=u'Organisme editeur', related_name='main_org')

    class Meta:
        abstract = True
        verbose_name = _('Site Preferences')
        app_label = 'coop_local'
