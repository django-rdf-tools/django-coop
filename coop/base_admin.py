# -*- coding:utf-8 -*-

from django.contrib import admin
from coop_local.models import *
from coop.person.admin import PersonAdmin
from coop.org.admin import OrganizationAdmin
from coop_tag.settings import get_class
from django.conf import settings

# -- Loading base models

admin.site.register(LinkProperty)

admin.site.register(PersonCategory)
admin.site.register(Person, PersonAdmin)

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationCategory)

if "coop.exchange" in settings.INSTALLED_APPS:
    from coop.exchange.admin import ExchangeAdmin
    admin.site.register(ExchangeMethod)
    admin.site.register(Exchange, ExchangeAdmin)


admin.site.unregister(get_class('tag'))
admin.site.register(get_class('tag'))
