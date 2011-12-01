#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import http
from django.utils import simplejson as json
from django.core import serializers
from django.views.generic.list import BaseListView

from models import Location

class JSONResponseMixin(object):
    def render_to_response(self, context):
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        json_serializer = serializers.get_serializer("json")()
        response = json_serializer.serialize(context['object_list'],
                                             ensure_ascii=False)
        return response

class JSONLocationView(JSONResponseMixin, BaseListView):
    model = Location
    def get_queryset(self):
        query = super(JSONLocationView, self).get_queryset()
        city = self.kwargs['city']
        address = self.kwargs['address']
        query = query.filter(city__icontains=city)
        if address:
            query = query.filter(adr1__icontains=address)
        return query

