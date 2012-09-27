# -*- coding:utf-8 -*-

import sys
from coop_local.local_settings import DEBUG
from coop_local.settings import DEBUG_SETTINGS

if DEBUG or ('runserver' in sys.argv):
    import firepython
    firepython.__api_version__ = '1.2'  # avoid known issue
    MIDDLEWARE_CLASSES = DEBUG_SETTINGS['middleware'] + [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        #'firepython.middleware.FirePythonDjango',
        ]
    INSTALLED_APPS = DEBUG_SETTINGS['apps'] + [
        'debug_toolbar',
        #'debug_toolbar_htmltidy',
        ]
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
        #'debug_toolbar_htmltidy.panels.HTMLTidyDebugPanel',
    ]
    DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}

else:
    INSTALLED_APPS = DEBUG_SETTINGS['apps'] + ['raven.contrib.django']
    MIDDLEWARE_CLASSES = DEBUG_SETTINGS['middleware'] + [
        'raven.contrib.django.middleware.Sentry404CatchMiddleware',
        ]
    DEBUG_SETTINGS['logging']['root'] = {
        'level': 'WARNING',
        'handlers': ['sentry'],
    }
    DEBUG_SETTINGS['logging']['handlers']['sentry'] = {
            'level': 'ERROR',
            'class': 'raven.contrib.django.handlers.SentryHandler',
       }
    DEBUG_SETTINGS['logging']['loggers']['raven'] = {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        }
    DEBUG_SETTINGS['logging']['loggers']['sentry.errors'] = {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        }
    LOGGING = DEBUG_SETTINGS['logging']
