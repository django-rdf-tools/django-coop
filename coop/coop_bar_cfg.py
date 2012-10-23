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
            for model_name in object_names:
                # objet  present dans le contexte ?
                object = context.get(model_name)
                if object and request and request.user.has_perm(perm + "_" + model_name, object):
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


def admin_articles(request, context):
    if request and request.user.is_staff:
        return make_link(reverse('admin:coop_local_article_changelist'), 'Articles', 'fugue/documents-stack.png',
            classes=['icon', 'alert_on_click'])


def load_commands(coop_bar):
    coop_bar.register([

        [django_admin, admin_articles],  # django_admin_navtree

        [   org_edit_link,
            org_view_link,
            org_save,
            org_edit_cancel_link,
            org_admin_link
        ],
        [   org_category_edit_link,
            org_category_view_link,
            org_save,
            org_category_edit_cancel_link
        ],

        [cms_edit, cms_view, cms_save, cms_cancel, django_admin_edit_article, cms_article_settings],

        [cms_new_article, ],

        [cms_new_newsletter, edit_newsletter, cancel_edit_newsletter, save_newsletter,
            change_newsletter_settings,
            schedule_newsletter, test_newsletter],

        [cms_media_library, cms_upload_image, cms_upload_doc],

        [log_out]
    ])

