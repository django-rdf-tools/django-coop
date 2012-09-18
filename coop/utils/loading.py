# -*- coding:utf-8 -*-

"""
Conditionally load models from coop.base_models or from coop_local.models.local_models
to make them globally available from coop_locals.models,
without patching django loading process

http://effbot.org/zone/import-confusion.htm

"""


from django.conf import settings
import logging
from django.core.exceptions import ImproperlyConfigured
import inspect
from django.db.models.base import Model as DjangoModel
from coop_local.models import local_models  # DO NOT REMOVE !!!

log = logging.getLogger('coop')


def import_class(cl):
    d = cl.rfind(".")
    classname = cl[d + 1:len(cl)]
    m = __import__(cl[0:d], globals(), locals(), [classname])
    return getattr(m, classname)


def relocalize_model(model_name, origin, target):
    class_name = str(origin.__name__) + '.' + model_name
    klass = import_class(class_name)
    setattr(target, model_name, klass)
    #log.debug('--> "%s" is now available from <%s>.' % (model_name, target.__name__))


def load_models(base_models, local_models, main_module):
    apps = {'local': [], 'base': [], 'other': []}
    for app in settings.BASE_COOP_LOCAL_MODELS:
        if app[0] in settings.INSTALLED_APPS:
            for model_name in app[1]:
                try:
                    # first, we try to load customized coop Models from local_models (they should have the same name)
                    relocalize_model(model_name, local_models, main_module)
                    apps['local'].append(model_name)
                except Exception, msg:
                    #log.debug('"%s" has not been customized in local_models...' % model_name)
                    # if it's not there, we assume we can load it from the base models
                    try:
                        relocalize_model(model_name, base_models, main_module)
                        apps['base'].append(model_name)

                    except Exception, msg:
                        raise ImproperlyConfigured('Unable to load "%s" from local or base models : %s' % (model_name, msg))

    # Looking for non-coop models also declared in coop_local
    custmodel_list = [(name, obj) for (name, obj) in inspect.getmembers(local_models, inspect.isclass) if (
                        hasattr(obj, '__class__')
                        and DjangoModel in obj.__mro__
                        and 'coop_local' in obj.__module__
                        and name not in apps['local']
                        and name not in apps['base']
                    )]

    for model_name, obj in custmodel_list:
        relocalize_model(model_name, local_models, main_module)
        apps['other'].append(model_name)

    #log.debug('Vanilla coop models installed : %s' % ', '.join([x[0] for x in custmodel_list]))

    log.debug('*** VANILLA COOP MODELS : %s' % ', '.join(apps['base']))
    log.debug('*** CUSTOMIZED COOP MODELS : %s' % ', '.join(apps['local']))
    log.debug('*** ADDITIONAL MODELS : %s' % ', '.join(apps['other']))
