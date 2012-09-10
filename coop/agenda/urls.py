from django.conf.urls.defaults import *

from coop.agenda import views


urlpatterns = patterns('',
    #url(r'^(?:calendar/)?$',
    url(r'^calendar/?$',
        view=views.today_view,
        name='agenda-today'),

    url(r'^calendar/(?P<year>\d{4})/$',
        view=views.year_view,
        name='agenda-yearly-view'),

    url(r'^calendar/(\d{4})/(0?[1-9]|1[012])/$',
        view=views.month_view,
        name='agenda-monthly-view'),

    url(r'^calendar/(\d{4})/(0?[1-9]|1[012])/([0-3]?\d)/$',
        view=views.day_view,
        name='agenda-daily-view'),

    url(r'^events/$',
        view=views.event_listing,
        name='agenda-events'),

    url(r'^calendar/(?P<slug>[\w-]+)/$',
        view=views.calendar_listing,
        name='agenda-calendar'),

    url(r'^events/add/$',
        view=views.add_event,
        name='agenda-add-event'),

    url(r'^events/(\d+)/$',
        view=views.event_view,
        name='agenda-event'),

    url(r'^events/mini/(\d+)/$',
        view=views.event_minimal_view,
        name='event-minimal-view'),  # CBV !!!

    url(r'^events/(\d+)/(\d+)/$',
        view=views.occurrence_view,
        name='agenda-occurrence'),
)
