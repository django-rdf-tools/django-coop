# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.template.loader import get_template
from django.template import Context
from coop_cms.settings import get_article_class
from django.conf import settings
from coop_bar.utils import make_link

from coop_cms.coop_bar_cfg import can_do

#can_do teste editable=true et que l'objet est presetn dans le contexte et que l'utilisateur a le droit sur ce droit

can_edit_organization = can_do('can_edit',['organization']) # methode du model (doit s'appeller can_edit_organization) + objet du contexte


@can_edit_organization
def edit_org(request, context):
    org = context.get('organization')
    url = reverse('org_detail', args=[org.slug])
    return make_link(url, _(u'Edit organization'), 'fugue/store.png', classes=['icon'])

# @can_post_event
# def post_event(request, context):
#     org = context.get('organization')
#     url = reverse('org_detail', args=[org.slug])
#     return make_link(url, _(u'Post new event'), 'fugue/calendar--plus.png.png',classes=['icon'])


def load_commands(coop_bar):
    coop_bar.register([
        [edit_org,]  # post_event]
    ])

    #coop_bar.register_header(cms_extra_js)
