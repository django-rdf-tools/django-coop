# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from coop_bar.utils import make_link
from coop.coop_bar_cfg import coop_perm
from coop_cms.coop_bar_cfg import can_add_article

can_edit_newsletter = coop_perm('can_edit', ['newsletter'])
can_edit = coop_perm('can_edit', ['article', 'newsletter'])  # pour activer le lien mediathèque


@can_add_article
def new_newsletter(request, context):
    if not context.get('edit_mode'):
        url = reverse('new_newsletter')
        return make_link(url, _(u'Create newsletter'), 'fugue/document--plus.png',
            classes=['alert_on_click', 'colorbox-form', 'icon'])


@can_edit_newsletter
def edit_newsletter(request, context):
    if not context.get('edit_mode'):
        newsletter = context.get('newsletter')
        return make_link(newsletter.get_edit_url(), _(u'Edit'), 'fugue/document--pencil.png', classes=['icon'])


@can_edit_newsletter
def cancel_edit_newsletter(request, context):
    if context.get('edit_mode'):
        newsletter = context.get('newsletter')
        return make_link(newsletter.get_absolute_url(), _(u'Cancel'), 'fugue/cross.png', classes=['icon'])


@can_edit_newsletter
def save_newsletter(request, context):
    # newsletter = context.get('newsletter')
    post_url = context.get('post_url')
    if context.get('edit_mode') and post_url:
        return make_link(post_url, _(u'Save'), 'fugue/tick.png', id="coopbar_save",
            classes=['icon', 'post-form'])


@can_edit_newsletter
def newsletter_settings(request, context):
    if not context.get('edit_mode'):
        newsletter = context.get('newsletter')
        url = reverse('newsletter_settings', kwargs={'newsletter_id': newsletter.id})
        return make_link(url, _(u'Newsletter settings'), 'fugue/gear.png',
            classes=['icon', 'colorbox-form', 'alert_on_click'])


#DEPRECATED
@can_edit_newsletter
def change_newsletter_template(request, context):
    if context.get('edit_mode'):
        newsletter = context.get('newsletter')
        url = reverse('change_newsletter_template', args=[newsletter.id])
        return make_link(url, _(u'Newsletter template'), 'fugue/application-blog.png',
            classes=['alert_on_click', 'colorbox-form', 'icon'])


###############


@can_edit_newsletter
def test_newsletter(request, context):
    newsletter = context.get('newsletter')
    url = reverse('test_newsletter', args=[newsletter.id])
    return make_link(url, _(u'Send test'), 'fugue/mail-at-sign.png',
        classes=['alert_on_click', 'colorbox-form', 'icon'])


@can_edit_newsletter
def schedule_newsletter(request, context):
    if not context.get('edit_mode'):
        newsletter = context.get('newsletter')
        url = reverse('schedule_newsletter_sending', args=[newsletter.id])
        return make_link(url, _(u'Schedule sending'), 'fugue/alarm-clock--arrow.png',
            classes=['alert_on_click', 'colorbox-form', 'icon'])

