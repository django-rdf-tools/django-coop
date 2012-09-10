#!/usr/bin/env python
import os
# import sys

from django.core import management
# from coop import management as coop_management
import coop.management

if __name__ == "__main__":
    # global management._commands
    if management._commands is None:
        management._commands = dict([(name, 'coop') for name in management.find_commands(coop.management.__path__[0])])
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coop.minimal_settings")


    management.execute_from_command_line()
