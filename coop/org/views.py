# # -*- coding:utf-8 -*-

from django.shortcuts import render_to_response
from coop_local.models import Organization, OrganizationCategory, Engagement, Role
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from coop.forms import OrganizationForm
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
    context = {'category': cat}
    context['org_list'] = org_list
    return render_to_response('org/org_category.html', context, RequestContext(request))


def org_detail_view(request, slug):
    context = {'editable': True}
    org = get_object_or_404(Organization, slug=slug)
    context['object'] = org
    #context['rss'] = cms_object.contact.get(category=6)
    context['adresses'] = cms_object.located.all()
    context['engagements'] = Engagement.objects.filter(organization=org)
    return render_to_response('org/org_detail.html', context, RequestContext(request))


@login_required
def edit_org(request, slug):
    logger = getLogger('default')
    org = get_object_or_404(Organization, slug=slug)
    if not request.user.has_perm('can_edit_org', org):
        raise PermissionDenied

    if request.method == "POST":
        form = OrganizationForm(request.POST, request.FILES, instance=org)
        forms_args = djaloha_utils.extract_forms_args(request.POST)
        djaloha_forms = djaloha_utils.make_forms(forms_args, request.POST)
        if form.is_valid() and all([f.is_valid() for f in djaloha_forms]):
            logger.error('formulaire valide')
            org = form.save()
            if cms_object.temp_logo:
                cms_object.logo = cms_object.temp_logo
                cms_object.temp_logo = ''
                cms_object.save()
            if djaloha_forms:
                [f.save() for f in djaloha_forms]
            messages.success(request, _(u'Your changes have been saved properly'))

            return HttpResponseRedirect(cms_object.get_absolute_url())
        else:
            logger.error('formulaire valide')
            messages.error(request, _(u"An error has occured."))

    else:
        from coop_bar.urls import bar
        if "pageSlide" not in bar.get_footer(request, RequestContext(request)):
            bar.register_footer(coop_bar_aloha_js)

        form = OrganizationForm(instance=org)

    context_dict = {
        'form': form,
        'editable': True,
        'edit_mode': True,
        'title': article.title,
        'draft': article.publication == models.BaseArticle.DRAFT,
        'cms_object': cms_object,
    }

    return render_to_response(
        get_article_template(article),
        context_dict,
        context_instance=RequestContext(request)
    )


@login_required
def cancel_edit_article(request, url):
    """if cancel_edit, delete the preview image"""
    article = get_object_or_404(get_article_class(), slug=url)
    if article.temp_logo:
        article.temp_logo = ''
        article.save()
    return HttpResponseRedirect(article.get_absolute_url())



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
