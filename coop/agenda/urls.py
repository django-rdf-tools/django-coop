from django.conf.urls.defaults import *

from coop.agenda import views


urlpatterns = patterns('coop.agenda.views',
    #url(r'^(?:calendar/)?$',
    url(r'^agenda/?$',
        'agenda_by_name',
        name='agenda-default'),

    url(r'^agenda/(?P<slug>[\w-]+)/$',
        'agenda_by_category',
        # 'agenda_by_name',
        name='agenda-default'),

    url(r'^agenda/category/(?P<slug>[\w-]+)/$',
        'event_category_view',
        name='agenda-event-category'),

    url(r'^agenda/(?P<year>\d{4})/$',
        'year_view',
        name='agenda-yearly-view'),

    url(r'^agenda/(\d{4})/(0?[1-9]|1[012])/$',
        'month_view',
        name='agenda-monthly-view'),

    url(r'^agenda/(\d{4})/(0?[1-9]|1[012])/([0-3]?\d)/$',
        'day_view',
        name='agenda-daily-view'),

    url(r'^evenements/$', 'event_listing',
        name='agenda-events'),

    url(r'^evenements/add/$',
        'add_event',
        name='agenda-add-event'),

    url(r'^evenements/(\d+)/$',
        'event_view',
        name='agenda-event'),

    url(r'^evenements/mini/(\d+)/$',
        'event_minimal_view',
        name='event-minimal-view'),  # CBV !!!

    url(r'^evenements/(\d+)/(\d+)/$',
        'occurrence_view',
        name='agenda-occurrence'),
)
