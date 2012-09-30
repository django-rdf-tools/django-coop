# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from coop_bar.utils import make_link
from django.contrib.contenttypes.models import ContentType


def coop_perm(perm, object_names):
    def inner_decorator(func):
        def wrapper(request, context):
            editable = context.get('editable')
            # objet editable en front-end ?
            if not editable:
                return
            for object_name in object_names:
                # objet  present dans le contexte ?
                object = context.get(object_name)
                if object and request and request.user.has_perm(perm + "_" + object_name, object):
                    yes_we_can = func(request, context)
                    if yes_we_can:
                        return yes_we_can
            return
        return wrapper
    return inner_decorator

# @can_post_event
# def post_event(request, context):
#     org = context.get('organization')
#     url = reverse('org_detail', args=[org.slug])
#     return make_link(url, _(u'Post new event'), 'fugue/calendar--plus.png.png',classes=['icon'])


from coop.org.coop_bar_links import *
from coop_cms.coop_bar_cfg import *


def load_commands(coop_bar):
    coop_bar.register([


        [django_admin,],  # django_admin_navtree

        [edit_org_link, view_org_link, org_save, org_edit_cancel_link, org_admin_link],

        [cms_edit, cms_view, cms_save, cms_cancel, django_admin_edit_article, cms_article_settings],

        [cms_new_article, ],

        [cms_new_newsletter, edit_newsletter, cancel_edit_newsletter, save_newsletter,
            change_newsletter_settings,
            schedule_newsletter, test_newsletter],

        [cms_media_library, cms_upload_image, cms_upload_doc],

        [log_out]
    ])

