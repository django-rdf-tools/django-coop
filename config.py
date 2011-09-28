# -*- coding:utf-8 -*-

from livesettings import config_register, ConfigurationGroup, PositiveIntegerValue, MultipleStringValue
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

not_to_be_mapped = ('south','livesettings','django_extensions','d2rq')

import settings
all_apps=[]
for m in settings.INSTALLED_APPS:
    if(not m.startswith('django.') and m not in not_to_be_mapped):
        all_apps.append((m,m))

if('d2rq' in settings.INSTALLED_APPS):

    DR2Q_MAPPING = ConfigurationGroup(
        'd2rq',               # key: internal name of the group to be created
        _('Configuration du mapper RDF'),  # name: verbose name which can be automatically translated
        ordering=0             # ordering: order of group in the list (default is 1)
    )

    config_register(MultipleStringValue(
        DR2Q_MAPPING,
        'MAPPED_APPS',
        description=_("Selection des applications"),
        help_text=_("Selectionnez les applications avec des donnees a publier en RDF"),
        choices=all_apps,
        default=""
    ))

if('coop_cms' in settings.INSTALLED_APPS):

    COOPTREE_MAPPING = ConfigurationGroup('coop_cms', _('Navigation'))

    # Another example of allowing the user to select from several values
    config_register(MultipleStringValue(
        COOPTREE_MAPPING,
        'CONTENT_APPS',
        description=_("Selection des applications"),
        help_text=_("Selectionnez des applications contenant des objets navigables"),
        choices=all_apps,
        default=""
    ))

