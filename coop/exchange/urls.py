# -*- coding:utf-8 -*-
from django.conf.urls.defaults import *
from django.views.generic.detail import DetailView
from django.views.generic import ListView

from coop_local.models import Exchange

# urlpatterns = patterns('',
#     url(r'^(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$', 
#         'coop.exchange.views.exchange_detail', 
#         name="exchange_detail"),
# )

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Exchange, template_name="exchange/exchange_list.html")),
    url(r'^(?P<slug>\d+)/$', 
        DetailView.as_view(
            model=Exchange,
            context_object_name="exchange",
            slug_field="id",
            template_name="exchange/exchange_detail.html"
            ),
            name="exchange_detail"),
    )
