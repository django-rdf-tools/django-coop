# -*- coding:utf-8 -*-

from django.contrib import admin
from coop_local.models import *
from coop.person.admin import PersonAdmin
from coop.org.admin import OrganizationAdmin
from coop.prefs.admin import SitePrefsAdmin
from django.conf import settings

# -- Loading base models

admin.site.register(LinkProperty)
admin.site.register(Role)
admin.site.register(PersonCategory)
admin.site.register(Person, PersonAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(SitePrefs, SitePrefsAdmin)


if "coop.exchange" in settings.INSTALLED_APPS:
    from coop.exchange.admin import ExchangeAdmin
    admin.site.register(ExchangeMethod)
    admin.site.register(Exchange, ExchangeAdmin)

if "coop_cms" in settings.INSTALLED_APPS:
    from coop.article.admin import CoopArticleAdmin
    from coop_cms.settings import get_article_class
    article_model = get_article_class()
    admin.site.unregister(article_model)
    admin.site.register(article_model, CoopArticleAdmin)

if "coop_tag" in settings.INSTALLED_APPS:
    from coop_tag.settings import get_class
    admin.site.unregister(get_class('tag'))
    admin.site.register(get_class('tag'))  # et ???

if 'forms_builder.forms' in settings.INSTALLED_APPS:
    from coop.admin import CoopFormAdmin
    from forms_builder.forms.models import Form
    admin.site.unregister(Form)
    admin.site.register(Form, CoopFormAdmin)
