# -*- coding:utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

def django_admin_command(request, context):
    if request.user.is_staff:
        return u'<a href="{0}">{1}</a>'.format(reverse("admin:index"), _('Admin'))

def load_commands(coop_bar):
    coop_bar.register_command(django_admin_command)
