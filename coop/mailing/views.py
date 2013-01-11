# -*- coding:utf-8 -*-
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.template import RequestContext
from django.core.exceptions import PermissionDenied
import sys
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from colorbox.decorators import popup_redirect
from coop_local.models import NewsletterSending, MailingList
from coop.mailing.utils import send_newsletter
from django.utils.log import getLogger
from datetime import datetime
from coop_local.models import Newsletter
from coop.mailing import forms
from django.core.urlresolvers import reverse
from soap import info as soap_info, lists

# TODO ces 2 references doivent sauter
from djaloha import utils as djaloha_utils
from coop_cms.views import coop_bar_aloha_js



def list(request, ml_id):
    """
    :ml_id MailingList id 
    """
    print request.META
    if request.META['REMOTE_ADDR'] in settings.INTERNAL_IPS or \
            (request.user.is_authenticated() and request.user.is_superuser):
        mailinglist = get_object_or_404(MailingList, id=ml_id)  
        return HttpResponse(mailinglist.subscription_list())
    else:
        raise Http404



@login_required
def edit_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    newsletter_form_class = forms.get_newsletter_form()

    if not request.user.has_perm('can_edit_newsletter', newsletter):
        raise PermissionDenied

    from coop_bar.urls import bar
    if "pageSlide" not in bar.get_footer(request, RequestContext(request)):
        bar.register_footer(coop_bar_aloha_js)

    if request.method == "POST":
        form = newsletter_form_class(request.POST, instance=newsletter)

        forms_args = djaloha_utils.extract_forms_args(request.POST)
        djaloha_forms = djaloha_utils.make_forms(forms_args, request.POST)

        if form.is_valid():  # and all([f.is_valid() for f in djaloha_forms]):
            newsletter = form.save()

            if djaloha_forms:
                [f.save() for f in djaloha_forms]

            messages.success(request, _(u'The newsletter has been saved properly'))

            return HttpResponseRedirect(reverse('coop_edit_newsletter', args=[newsletter.id]))
    else:
        form = newsletter_form_class(instance=newsletter)

    context_dict = {
        'form': form,
        'post_url': reverse('coop_edit_newsletter', args=[newsletter.id]),
        'editable': True,
        'edit_mode': True,
        'title': newsletter.subject,
        'newsletter': newsletter,
    }

    return render_to_response(
        newsletter.get_template_name(),
        context_dict,
        context_instance=RequestContext(request)
    )


@login_required
@popup_redirect
def new_newsletter(request, newsletter_id=None):

    #ct = ContentType.objects.get_for_model(Article)
    #perm = '{0}.add_{1}'.format(ct.app_label, ct.model)

    #if not request.user.has_perm(perm):
    #    raise PermissionDenied

    if newsletter_id:
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    else:
        newsletter = None

    try:
        if request.method == "POST":
            form = forms.NewNewsletterForm(request.user, request.POST, instance=newsletter)
            if form.is_valid():
                #article.template = form.cleaned_data['template']
                newsletter = form.save()
                return HttpResponseRedirect(newsletter.get_edit_url())
        else:
            form = forms.NewNewsletterForm(request.user, instance=newsletter)

        return render_to_response(
            'coop_cms/popup_new_newsletter.html',
            locals(),
            context_instance=RequestContext(request)
        )
    except Exception, msg:
        # print "#", msg
        raise




def view_newsletter(request, newsletter_id):

    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    context_dict = {
        'title': newsletter.subject, 'newsletter': newsletter,
        'editable': request.user.is_authenticated()
    }

    return render_to_response(
        newsletter.get_template_name(),
        context_dict,
        context_instance=RequestContext(request)
    )


@login_required
@popup_redirect
def change_newsletter_template(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if not request.user.has_perm('can_edit_newsletter', newsletter):
        raise PermissionDenied

    if request.method == "POST":
        form = forms.NewsletterTemplateForm(newsletter, request.user, request.POST)
        if form.is_valid():
            newsletter.template = form.cleaned_data['template']
            newsletter.save()
            return HttpResponseRedirect(newsletter.get_edit_url())
    else:
        form = forms.NewsletterTemplateForm(newsletter, request.user)

    return render_to_response(
        'coop_cms/popup_change_newsletter_template.html',
        {'form': form, 'newsletter': newsletter},
        context_instance=RequestContext(request)
    )


@login_required
@popup_redirect
def test_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if not request.user.has_perm('can_edit_newsletter', newsletter):
        raise PermissionDenied

    dests = settings.COOP_CMS_TEST_EMAILS

    if request.method == "POST":
        try:
            nb_sent = send_newsletter(newsletter, dests)

            messages.success(request,
                _(u"The test email has been sent to {0} addresses: {1}").format(nb_sent, u', '.join(dests)))
            return HttpResponseRedirect(newsletter.get_edit_url())
        except Exception, msg:
            messages.error(request, _(u"An error has occured.") + u'<br>' + unicode(msg))
            logger = getLogger('django.request')
            logger.error('Internal Server Error: %s' % request.path,
                exc_info=sys.exc_info,
                extra={
                    'status_code': 500,
                    'request': request
                }
            )
            return HttpResponseRedirect(newsletter.get_edit_url())

    return render_to_response(
        'coop_cms/popup_test_newsletter.html',
        {'newsletter': newsletter, 'dests': dests},
        context_instance=RequestContext(request)
    )


@login_required
@popup_redirect
def schedule_newsletter_sending(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    instance = NewsletterSending(newsletter=newsletter)

    if request.method == "POST":
        form = forms.NewsletterSchedulingForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(newsletter.get_edit_url())
    else:
        form = forms.NewsletterSchedulingForm(instance=instance, initial={'scheduling_dt': datetime.now()})

    return render_to_response(
        'coop_cms/popup_schedule_newsletter_sending.html',
        {'newsletter': newsletter, 'form': form},
        context_instance=RequestContext(request)
    )
