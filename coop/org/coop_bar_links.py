# -*- coding:utf-8 -*-

from coop.coop_bar_cfg import coop_perm
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from coop_bar.utils import make_link

can_edit_org = coop_perm('can_edit', ['organization'])
# La methode du model doit s'appeller "can_edit_orgnization")

@can_edit_org
def edit_org_link(request, context):
    print 'loading link : edit_org_link'
    if not context.get('edit_mode'):
        org = context.get('organization')
        url = reverse('org_edit', args=[org.slug])
        return make_link(url, _(u'Edit organization'), 'fugue/store.png', classes=['icon'])


@can_edit_org
def view_org_link(request, context):
    print 'loading link : org_detail_link'
    if context.get('edit_mode'):
        org = context['organization']
        return make_link(org.get_cancel_url(), _(u'View'), 'fugue/eye.png',
            classes=['alert_on_click', 'icon', 'show-clean'])


@can_edit_org
def org_save(request, context):
    if context.get('edit_mode'):
        #No link, will be managed by catching the js click event
        return make_link('', _(u'Save'), 'fugue/tick.png', id="coopbar_save",
            classes=['show-dirty', 'icon'])


@can_edit_org
def org_edit_cancel_link(request, context):
    print 'org_edit_cancel_link'
    if context.get('edit_mode'):
        org = context['organization']
        return make_link(org.get_cancel_url(), _(u'Cancel'), 'fugue/cross.png',
            classes=['alert_on_click', 'icon', 'show-dirty'])


def org_admin_link(request, context):
    if request and request.user.is_staff and 'organization' in context:
        if not context.get('edit_mode'):
            org = context['organization']
            view_name = 'admin:%s_%s_change' % ('coop_local', 'organization')
            return make_link(reverse(view_name, args=[org.id]), _(u"Edit via admin"), 'fugue/application-form.png',
                classes=['icon', 'alert_on_click'])
