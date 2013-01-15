
# -*- coding:utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response, redirect
from coop_local.models import Project
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse
import json


def projects_list(request):
    context = {}
    context['projets'] = Project.objects.all()
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
                countries[project.zone.id] = {
                    "type": "Feature",
                    "properties": {
                        "name": project.zone.label,
                        "popupContent": u"<h4>" + project.zone.label + "</h4><p class='map_link_project'>\
                        <a href='" + project.get_absolute_url() + u"'>" + project.title + "</a></p>"
                        },
                    "geometry": {
                        "type": "MultiPolygon",
                        "coordinates": project.zone.polygon.coords
                        }
                    }
            else:
                countries[project.zone.id]["properties"]["popupContent"] += u"\n<p class='map_link_project'>\
                <a href='" + project.get_absolute_url() + u"'>" + project.title + "</a></p>"
    projects = {"type": "FeatureCollection", "features": countries.values()}
    return HttpResponse(json.dumps(projects), mimetype="application/json")
