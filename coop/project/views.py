
# -*- coding:utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response, redirect
from coop_local.models import Project
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse
import json
from coop.views import default_region


def projects_list(request):
    context = {}
    context['projects'] = Project.objects.all()
    context['region'] = default_region()
    return render_to_response('project/projects_list.html', context, RequestContext(request))


def project_detail(request, id):
    context = {}
    context['item'] = get_object_or_404(Project, id=id)
    return render_to_response('project/project_detail.html', context, RequestContext(request))


def projects_map(request):
    countries = {}
    qs = Project.objects.all()
    for project in qs:
        if project.zone:
            if not project.zone.id in countries:
                countries[project.zone.id] = project.zone_geoJson()[0]
            else:
                countries[project.zone.id]["properties"]["popupContent"] += u"\n<p class='map_link_project'>\
                <a href='" + project.get_absolute_url() + u"'>" + project.title + "</a></p>"
    projects = {"type": "FeatureCollection", "features": countries.values()}
    return HttpResponse(json.dumps(projects), mimetype="application/json")


