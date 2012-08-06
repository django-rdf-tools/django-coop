# -*- coding:utf-8 -*-

from django.contrib import admin
from coop_local.models import *
from coop.person.admin import PersonAdmin
from coop.exchange.admin import ExchangeAdmin
from coop.org.admin import OrganizationAdmin
from coop.tag.admin import CoopTagTreeAdmin
from coop_tag.settings import get_class

# -- Loading base models

admin.site.register(LinkProperty)

admin.site.register(PersonCategory)
admin.site.register(Person, PersonAdmin)
admin.site.register(Role, CoopTagTreeAdmin)

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationCategory)

admin.site.register(ExchangeMethod)
admin.site.register(Exchange, ExchangeAdmin)


admin.site.unregister(get_class('tag'))
admin.site.register(get_class('tag'), CoopTagTreeAdmin)
