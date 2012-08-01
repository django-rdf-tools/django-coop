# -*- coding:utf-8 -*-

from django.contrib import admin
from coop_local.models import *
from coop.person.admin import PersonAdmin
from coop.exchange.admin import ExchangeAdmin
from coop.org.admin import OrganizationAdmin, RoleAdmin


# -- Loading base models

admin.site.register(PersonCategory)
admin.site.register(Person, PersonAdmin)
admin.site.register(Role, RoleAdmin)

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationCategory)

admin.site.register(ExchangeMethod)
admin.site.register(Exchange, ExchangeAdmin)


