# -*- coding:utf-8 -*-

from django.contrib import admin
from coop_local.models import *
from coop.person.admin import PersonAdmin
from coop.org.admin import OrganizationAdmin
from coop.prefs.admin import SitePrefsAdmin
from coop_geo.admin import LocationAdmin, AreaAdmin
from django.conf import settings

# -- Loading base models

admin.site.register(LinkProperty)
admin.site.register(Link)
admin.site.register(Role)
admin.site.register(PersonCategory)
admin.site.register(Person, PersonAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationCategory)
admin.site.register(OrgRelationType)
admin.site.register(SitePrefs, SitePrefsAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Area, AreaAdmin)

if "coop.project" in settings.INSTALLED_APPS:
    from coop.project.admin import ProjectAdmin
    admin.site.register(Project, ProjectAdmin)
    admin.site.register(ProjectCategory)

if "coop.mailing" in settings.INSTALLED_APPS:
    from coop.mailing.admin import MailingListAdmin, NewsletterAdmin
    admin.site.register(MailingList, MailingListAdmin)
    admin.site.register(Newsletter, NewsletterAdmin)

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
    admin.site.register(get_class('tag'))  # TODO find out why this hack has to be there !!!

if 'forms_builder.forms' in settings.INSTALLED_APPS:
    from coop.admin import CoopFormAdmin
    from forms_builder.forms.models import Form
    admin.site.unregister(Form)
    admin.site.register(Form, CoopFormAdmin)
