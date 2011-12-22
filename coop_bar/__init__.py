# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

VERSION = (0, 1)

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
#    if VERSION[2]:
#        version = '%s.%s' % (version, VERSION[2])
#    if VERSION[3] != "final":
#        version = '%s%s%s' % (version, VERSION[3], VERSION[4])
    return version

__version__ = get_version()


from django.utils.importlib import import_module
from django.conf import settings

class CoopBar:
    __we_are_all_one = {}
    
    def __init__(self):
        self.__dict__ = self.__we_are_all_one #Borg pattern
        
        self._callbacks = []
        
        for app in settings.INSTALLED_APPS:
            try:
                #load dynamically the admin_bar module of all apps
                app_admin_bar_module = import_module(app+'.coop_bar_cfg')
                if hasattr(app_admin_bar_module, 'load_commands'):
                    #call the load_commands function in this module
                    #This function should call the AdminBar:register_command for
                    #every item it want to insert in the bar
                    loader_fct = getattr(app_admin_bar_module, 'load_commands')
                    loader_fct(self)
            except ImportError:
                pass
        
    def register_command(self, callback):
        self._callbacks.append(callback)
                
    def get_commands(self, request, context):
        commands = []
        for c in self._callbacks:
            #when a page wants to display the admin_bar
            #calls the registred callback in order to know what to display
            html = c(request, context)
            if html:
                commands.append(html)
        return commands
    