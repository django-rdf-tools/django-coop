# -*- coding:utf-8 -*-

# WARNING : This is bootstraping code , DO NOT CHANGE ANYTHING
# DO NOT add custom models here , add them in local_models.py and they'll be loaded

import sys
from coop.utils.loading import load_models
from coop import base_models
from coop_local.models import local_models

main_module = sys.modules[__name__]

load_models(base_models, local_models, main_module)

# TaggableManager is only available when TaggedItem is loaded
# so we add tags fields after loading all the coop_local models

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

if "coop_tag" in settings.INSTALLED_APPS:
    from coop_tag.managers import TaggableManager
    # from coop_local.models import TaggedItem
    t = TaggableManager(through=TaggedItem,
            blank=True, verbose_name=_(u'Tags'),
            help_text="Une liste de tags avec des virgules")
    t.contribute_to_class(Organization, "tags")
    t.contribute_to_class(Person, "tags")
    if "coop_cms" in settings.INSTALLED_APPS:
        t.contribute_to_class(Article, "tags")
    if "coop.exchange" in settings.INSTALLED_APPS:
        t.contribute_to_class(Exchange, "tags")
    if "coop.agenda" in settings.INSTALLED_APPS:
        t.contribute_to_class(Event, "tags")


