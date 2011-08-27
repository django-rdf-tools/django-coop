# -*- coding:utf-8 -*-

from livesettings import config_register, ConfigurationGroup, PositiveIntegerValue, MultipleStringValue
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType


# 
# banned = ('auth','django','contenttypes','south','sessions','admin','d2rq')
# done = []
# AVAILABLE_MODELS = []
# all_models = ContentType.objects.exclude(app_label__in=banned).order_by('app_label')
# for a in all_models:
#     if(a.app_label not in done):
#         AVAILABLE_MODELS.append((
#             a.app_label , tuple((x.model,x.name) for x in all_models.filter(app_label=a.app_label))
#             ))
#     done.append(a.app_label)


not_to_be_mapped = ('south','livesettings','django_extensions','d2rq')

import settings
all_apps=[]
for m in settings.INSTALLED_APPS:
    if(not m.startswith('django.') and m not in not_to_be_mapped):
        all_apps.append((m,m))

# First, setup a grup to hold all our possible configs
DR2Q_MAPPING = ConfigurationGroup(
    'd2rq',               # key: internal name of the group to be created
    _('Configuration du mapper RDF'),  # name: verbose name which can be automatically translated
    ordering=0             # ordering: order of group in the list (default is 1)
    )

# Another example of allowing the user to select from several values
config_register(MultipleStringValue(
        DR2Q_MAPPING,
        'MAPPED_APPS',
        description=_("Selection des applications"),
        help_text=_("Selectionnez les applications avec des donnees a publier en RDF"),
        choices=all_apps,
        default=""
    ))