# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand
from django.utils.crypto import get_random_string
from django.utils.importlib import import_module
import os
from optparse import make_option


class Command(TemplateCommand):
    help = _(u"Creates a COOP project directory structure for the given "
            "project name in the current directory or optionally in the "
            "given directory.")

    option_list = TemplateCommand.option_list + (
        make_option('--redis_port',
                    action='store', dest='redis', default=6379,
                    help=_(u'Please set the redis port the application will used (default value is 6379')),
        make_option('--redis_bin',
                    action='store', dest='redis_bin', default='/opt/redis/bin/',
                    help=_(u'Please set the redis bin directory (default value is /opt/redis/bin/')),

        make_option('--domain',
                    action='store', dest='domain', default='localhost:8000',
                    help=_(u'Please set he domain name of your coop application (default value is localhost:8000/')),


        )

    def handle(self, project_name=None, target=None, *args, **options):
        if project_name is None:
            raise CommandError("you must provide a project name")

        # Check that the project_name cannot be imported.
        try:
            import_module(project_name)
        except ImportError:
            pass
        else:
            raise CommandError("%r conflicts with the name of an existing "
                               "Python module and cannot be used as a "
                               "project name. Please try another name." %
                               project_name)

        # Create a random SECRET_KEY hash to put it in the main settings.
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        options['secret_key'] = get_random_string(50, chars)

        import coop
        coop_dir = coop.__path__[0]

        # options dict is add to the context. Thus it is used to add new template
        # variables. Here 'template' is set 'hardy'
        options['template'] = os.path.join(coop_dir, 'templates', 'project_template')
        options['project_alldirs'] = os.path.split(coop_dir)[0]
        # For supervisor.conf file
        options['extensions'].extend(['conf', 'json', 'txt'])
        options['virtualenv'] = os.getenv('VIRTUAL_ENV')
        options['nice_name'] = project_name.title()
        p = os.popen('which runinenv.sh', "r")
        options['runinenv'] = p.readline().replace('\n', '')
        p.close()

        super(Command, self).handle('project', project_name, target, **options)
