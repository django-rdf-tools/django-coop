from django.conf.urls.defaults import *

from coop.agenda import views


urlpatterns = patterns('',
    #url(r'^(?:calendar/)?$',
    url(r'^agenda/?$',
        view=views.agenda_by_name,
        name='agenda-default'),

    url(r'^agenda/(?P<slug>[\w-]+)/$',
        view=views.agenda_by_name,
        name='agenda-default'),

    url(r'^agenda/(?P<year>\d{4})/$',
        view=views.year_view,
        name='agenda-yearly-view'),

    url(r'^agenda/(\d{4})/(0?[1-9]|1[012])/$',
        view=views.month_view,
        name='agenda-monthly-view'),

    url(r'^agenda/(\d{4})/(0?[1-9]|1[012])/([0-3]?\d)/$',
        view=views.day_view,
        name='agenda-daily-view'),

    url(r'^evenements/$',
        view=views.event_listing,
        name='agenda-events'),

    url(r'^evenements/add/$',
        view=views.add_event,
        name='agenda-add-event'),

    url(r'^evenements/(\d+)/$',
        view=views.event_view,
        name='agenda-event'),

    url(r'^evenements/mini/(\d+)/$',
        view=views.event_minimal_view,
        name='event-minimal-view'),  # CBV !!!

    url(r'^evenements/(\d+)/(\d+)/$',
        view=views.occurrence_view,
        name='agenda-occurrence'),
)
