# # -*- coding:utf-8 -*-

from django.shortcuts import render_to_response
from coop_local.models import Organization, OrganizationCategory, Engagement, Role
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from coop.org.forms import OrganizationForm, OrganizationCategoryForm
from django.contrib.auth.decorators import login_required
from logging import getLogger
from django.core.exceptions import ValidationError, PermissionDenied
from djaloha import utils as djaloha_utils
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden
import coop_bar
from coop_cms.views import coop_bar_aloha_js


def org_category_detail(request, slug):
    cat = get_object_or_404(OrganizationCategory, slug=slug)
    org_list = Organization.objects.filter(category=cat)
    context = {'org_category': cat}
    context['org_list'] = org_list
    return render_to_response('org/org_category.html', context, RequestContext(request))


def org_detail(request, slug):
    context = {'editable': True}
    org = get_object_or_404(Organization, slug=slug, sites__id=settings.SITE_ID)
    context['organization'] = org
    context['adresses'] = org.located.all()
    context['engagements'] = Engagement.objects.filter(organization=org)
    return render_to_response('org/org_detail.html', context, RequestContext(request))


@login_required
def org_edit(request, slug):
    logger = getLogger('default')
    organization = get_object_or_404(Organization, slug=slug, sites__id=settings.SITE_ID)  # model
    if not request.user.has_perm('can_edit_org', organization):  # model
        raise PermissionDenied

    if request.method == "POST":
        form = OrganizationForm(request.POST, request.FILES, instance=organization)
        forms_args = djaloha_utils.extract_forms_args(request.POST)
        djaloha_forms = djaloha_utils.make_forms(forms_args, request.POST)
        if form.is_valid() and all([f.is_valid() for f in djaloha_forms]):
            logger.error('formulaire valide')
            organization = form.save()
            # if organization.temp_logo:
            #     organization.logo = organization.temp_logo
            #     organization.temp_logo = ''
            #     organization.save()
            if djaloha_forms:
                [f.save() for f in djaloha_forms]
            messages.success(request, _(u'Your changes have been saved properly'))

            return HttpResponseRedirect(organization.get_absolute_url())
        else:

            # import pdb
            # pdb.set_trace()
            for f in form.errors.keys():
                logger.error(u'FORM ERROR | ' + unicode(f) + u' : ' + unicode(form.errors[f][0]))
            messages.error(request, _(u"An error has occured."))

    else:
        from coop_bar.urls import bar
        if "pageSlide" not in bar.get_footer(request, RequestContext(request)):
            bar.register_footer(coop_bar_aloha_js)
        form = OrganizationForm(instance=organization)

    context_dict = {
        'form': form,
        'editable': True,
        'edit_mode': True,
        'title': organization.title,
        'organization': organization,
    }

    return render_to_response(
        'org/org_detail.html',
        context_dict,
        context_instance=RequestContext(request)
    )


@login_required
def org_category_edit(request, slug):
    logger = getLogger('default')
    org_category = get_object_or_404(OrganizationCategory, slug=slug)  # model
    if not request.user.has_perm('can_edit_org_category', org_category):  # model
        raise PermissionDenied

    if request.method == "POST":
        form = OrganizationCategoryForm(request.POST, request.FILES, instance=org_category)
        forms_args = djaloha_utils.extract_forms_args(request.POST)
        djaloha_forms = djaloha_utils.make_forms(forms_args, request.POST)
        if form.is_valid() and all([f.is_valid() for f in djaloha_forms]):
            logger.error('formulaire valide')
            org_category = form.save()
            if djaloha_forms:
                [f.save() for f in djaloha_forms]
            messages.success(request, _(u'Your changes have been saved properly'))
            return HttpResponseRedirect(org_category.get_absolute_url())
        else:
            for f in form.errors.keys():
                logger.error(u'FORM ERROR | ' + unicode(f) + u' : ' + unicode(form.errors[f][0]))
            messages.error(request, _(u"An error has occured."))
    else:
        from coop_bar.urls import bar
        if "pageSlide" not in bar.get_footer(request, RequestContext(request)):
            bar.register_footer(coop_bar_aloha_js)
        form = OrganizationCategoryForm(instance=org_category)

    context_dict = {
        'form': form,
        'editable': True,
        'edit_mode': True,
        'title': org_category.label,  # ?
        'org_category': org_category,
    }

    return render_to_response(
        'org/org_category.html',
        context_dict,
        context_instance=RequestContext(request)
    )




@login_required
def org_edit_cancel(request, slug):
    """if cancel_edit, delete the preview image"""
    organization = get_object_or_404(Organization, slug=slug, sites__id=settings.SITE_ID)
    # if organization.temp_logo:
    #     organization.temp_logo = ''
    #     organization.save()
    return HttpResponseRedirect(organization.get_absolute_url())


@login_required
def org_category_edit_cancel(request, slug):
    org_category = get_object_or_404(OrganizationCategory, slug=slug, sites__id=settings.SITE_ID)
    return HttpResponseRedirect(org_category.get_absolute_url())


def org_list(request):
    context = {}
    context['org_list'] = Organization.objects.filter(active=True)
    return render_to_response('org/org_list.html', context, RequestContext(request))


def role_detail(request, slug):
    context = {}
    role = Role.objects.get(slug=slug)
    context['object'] = role
    context['engagements'] = Engagement.objects.filter(role=role).select_related('person').order_by('person__last_name')
    return render_to_response('org/role_detail.html', context, RequestContext(request))


def global_map(request):
    context = {}
    context['initiatives'] = Organization.objects.filter(active=True)
    return render_to_response('org/org_global_map.html',
                              context, RequestContext(request))

def leaflet(request):
    context = {}
    context['org_list'] = Organization.objects.filter(active=True)
    return render_to_response('org/org_carto.html', context, RequestContext(request))
