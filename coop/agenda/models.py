# -*- coding:utf-8 -*-

from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django_extensions.db import fields as exfields
from dateutil import rrule
from django.db.models.loading import get_model
from coop.models import URIModel
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings
import rdflib
from django.template.defaultfilters import date as _date
from datetime import datetime


class BaseCalendar(URIModel):
    title = models.CharField(_('title'), blank=True, max_length=250)
    description = models.TextField(_(u'description'), blank=True)
    slug = exfields.AutoSlugField(populate_from='title')

    class Meta:
        verbose_name = _('calendar')
        verbose_name_plural = _('calendars')
        abstract = True
        app_label = 'coop_local'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('agenda-default', args=[self.slug])

    rdf_type = settings.NS.vcal.Vcalendar
    base_mapping = [
        ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
        ('single_mapping', (settings.NS.dct.created, 'created'), 'single_reverse'),
        ('single_mapping', (settings.NS.dct.title, 'title'), 'single_reverse'),
        ('single_mapping', (settings.NS.dct.description, 'description'), 'single_reverse'),

        ('component_mapping', (settings.NS.vcal.component, ''), 'component_mapping_reverse'),

    ]

    def component_mapping(self, rdfPred, djF, lang=None):
        events = models.get_model('coop_local', 'event').objects.filter(calendar=self)
        res = []
        for e in events:
            res.append((rdflib.URIRef(self.uri), rdfPred, rdflib.URIRef(e.uri)))
        return res

    def component_mapping_reverse(self, g, rdfPred, rdfEnd, lang=None):
        values = list(g.objects(rdflib.term.URIRef(self.uri), rdfPred))
        m = models.get_model('coop_local', 'event')
        for v in values:
            event, created = m.objects.get_or_create(uri=str(v))
            event.calendar = self
            event.save()


class BaseEventCategory(models.Model):
    """
    Simple ``Event`` classification.
    """
    # abbr = models.CharField(_('abbreviation'), max_length=4, unique=True)  #varennes
    label = models.CharField(_('label'), max_length=50)
    slug = exfields.AutoSlugField(populate_from='label')

    class Meta:
        verbose_name = _('event category')
        verbose_name_plural = _('event categories')
        abstract = True
        app_label = 'coop_local'

    def __unicode__(self):
        return self.label

    @models.permalink
    def get_absolute_url(self):
        return ('agenda-event-category', [str(self.slug)])

    def events(self):
        return self.event_set.all()
        

class BaseEvent(URIModel):
    """
    Container model for general metadata and associated ``Occurrence`` entries.
    """
    title = models.CharField(_('title'), max_length=120)
    description = models.TextField(_(u'description'), blank=True)
    slug = exfields.AutoSlugField(populate_from='title')
    event_type = models.ForeignKey('coop_local.EventCategory', verbose_name=_('event type'))  # TODO rename category !!!
    calendar = models.ForeignKey('coop_local.Calendar', verbose_name=_('calendar'))

    # Linking to local objects
    organization = models.ForeignKey('coop_local.Organization', null=True, blank=True, verbose_name=_('organization'), related_name=_('publisher organization'))
    organizations = models.ManyToManyField('coop_local.Organization', null=True, blank=True, verbose_name=_('organizations'), related_name=_('other organizations'))

    person = models.ForeignKey('coop_local.Person', null=True, blank=True, verbose_name=_('author'))
    if "coop_geo" in settings.INSTALLED_APPS:
        location = models.ForeignKey('coop_local.Location', null=True, blank=True, verbose_name=_('location'))
        remote_location_uri = models.URLField(_('remote location URI'), blank=True, max_length=255)
        remote_location_label = models.CharField(_(u'remote location label'),
                                                max_length=250, blank=True, null=True,
                                                help_text=_(u'fill this only if the location record is not available locally'))

    # Linking to remote objects
    remote_person_uri = models.URLField(_('remote person URI'), blank=True, max_length=255)
    remote_person_label = models.CharField(_(u'remote person label'),
                                                max_length=250, blank=True, null=True,
                                                help_text=_(u'fill this only if the person record is not available locally'))
    remote_organization_uri = models.URLField(_('remote organization URI'), blank=True, max_length=255)
    remote_organization_label = models.CharField(_(u'remote organization label'),
                                                max_length=250, blank=True, null=True,
                                                help_text=_(u'fill this only if the organization record is not available locally'))

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ('title', )
        abstract = True
        app_label = 'coop_local'

    def label(self):
        return self.title

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('agenda-event', [str(self.id)])

    @property
    def linked_articles(self):
        linked_items = self.dated_set.all()
        if linked_items:
            result = []
            for item in linked_items:
                result.append(item.content_object)
            return result    
        else:
            return None

    def add_occurrences(self, start_time, end_time, **rrule_params):
        """
        Add one or more occurences to the event using a comparable API to
        ``dateutil.rrule``.

        If ``rrule_params`` does not contain a ``freq``, one will be defaulted
        to ``rrule.DAILY``.

        Because ``rrule.rrule`` returns an iterator that can essentially be
        unbounded, we need to slightly alter the expected behavior here in order
        to enforce a finite number of occurrence creation.

        If both ``count`` and ``until`` entries are missing from ``rrule_params``,
        only a single ``Occurrence`` instance will be created using the exact
        ``start_time`` and ``end_time`` values.
        """
        rrule_params.setdefault('freq', rrule.DAILY)

        if 'count' not in rrule_params and 'until' not in rrule_params:
            self.occurrence_set.create(start_time=start_time, end_time=end_time)
        else:
            delta = end_time - start_time
            for ev in rrule.rrule(dtstart=start_time, **rrule_params):
                self.occurrence_set.create(start_time=ev, end_time=ev + delta)

    def upcoming_occurrences(self):
        """
        Return all occurrences that are set to start on or after the current
        time.
        """
        return self.occurrence_set.filter(start_time__gte=datetime.now())

    def next_occurrence(self):
        """
        Return the single occurrence set to start on or after the current time
        if available, otherwise ``None``.
        """
        upcoming = self.upcoming_occurrences()
        return upcoming and upcoming[0] or None

    def daily_occurrences(self, dt=None):
        """
        Convenience method wrapping ``Occurrence.objects.daily_occurrences``.
        """
        return get_model('coop_local', 'Occurrence').objects.daily_occurrences(dt=dt, event=self)


    # RDF stuffs
    # Attention il faut tenir compte des occurences.... ca complique un peu


    rdf_type = settings.NS.vcal.Vevent
    base_mapping = [
        ('single_mapping', (settings.NS.dct.created, 'created'), 'single_reverse'),
        ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
        ('single_mapping', (settings.NS.vcal.summary, 'title'), 'single_reverse'),
        ('single_mapping', (settings.NS.vcal.description, 'description'), 'single_reverse'),
 
        ('local_or_remote_mapping', (settings.NS.vcal.contact, 'person'), 'local_or_remote_reverse'),
        ('local_or_remote_mapping', (settings.NS.vcal.organizer, 'organization'), 'local_or_remote_reverse'),
        ('local_or_remote_mapping', (settings.NS.locn.location, 'location'), 'local_or_remote_reverse'),

        ('multi_mapping', (settings.NS.dct.subject, 'tags'), 'multi_reverse'),
        ('multi_mapping', (settings.NS.vcal.attendee, 'organizations'), 'multi_reverse'),

        ('article_mapping', (settings.NS.dct.relation, 'linked_articles'), 'article_mapping_reverse'),
        ('category_mapping', (settings.NS.vcal.categories, 'event_type'), 'category_mapping_reverse'),
        ('occurence_mapping', (settings.NS.vcal.dtstart, settings.NS.vcal.dtend), 'occurence_mapping_reverse'),
    ]


    def article_mapping(self, rdfPred, djF, datatype=None, lang=None):
        if getattr(self, djF) == None:
            return [] 
        else:
            values = getattr(self, djF)
            return self.multi_mapping_base(values, rdfPred, datatype, lang)


    def article_mapping_reverse(self, g, rdfPred, djField, lang=None):
        articles = list(g.objects(rdflib.term.URIRef(self.uri), rdfPred))
        model_article = models.get_model('coop_local', 'article')
        model_dated = models.get_model('coop_local', 'dated')

        for a in articles:
            ar = model_article.get_or_create_from_rdf(uri=str(a))
            new_dated = model_dated(content_object=ar, event=self)
            new_dated.save()


    def category_mapping(self, rdfPred, djF, lang=None):
        value = getattr(self, djF).label
        return [(rdflib.term.URIRef(self.uri), rdfPred, rdflib.term.Literal(value))]

    def category_mapping_reverse(self, g, rdfPred, djField, lang=None):
        values = list(g.objects(rdflib.term.URIRef(self.uri), rdfPred))
        m = models.get_model('coop_local', 'eventcategory')
        if len(values) == 1:
            value = values[0]
            try:
                djValue = m.objects.get(label=value)
                setattr(self, djField, djValue)
            except m.DoesNotExist:
                pass

    def occurence_mapping(self, rdfStart, rdfEnd, lang=None):
        m = models.get_model('coop_local', 'occurrence')
        occurrences = m.objects.filter(event=self)
        if len(occurrences) == 1:  # ouf rien à faire
            occurrence = occurrences[0]
            return [(rdflib.term.URIRef(self.uri), rdfStart, rdflib.term.Literal(occurrence.start_time)),
                    (rdflib.term.URIRef(self.uri), rdfEnd, rdflib.term.Literal(occurrence.end_time))]
        elif len(occurrences) == 0:
            return []
        else:  # On gère les occurrences à minima et en trichant un peu on modifie l'uri stockée
            i = 0
            res = []
            for occurrence in occurrences:
                i += 1
                uri = self.uri + '#%s' % i
                res.append((rdflib.term.URIRef(uri), settings.NS.rdf.type, self.rdf_type))
                res.append((rdflib.term.URIRef(uri), settings.NS.dct.modified, self.modified))
                res.append((rdflib.term.URIRef(uri), rdfStart, rdflib.term.Literal(occurrence.start_time)))
                res.append((rdflib.term.URIRef(uri), rdfEnd, rdflib.term.Literal(occurrence.end_time)))
            return res  # en attendant meiux

    def occurence_mapping_reverse(self, g, rdfStart, rdfEnd, lang=None):
        start = list(g.objects(rdflib.term.URIRef(self.uri), rdfStart))
        m = models.get_model('coop_local', 'occurrence')

        if len(start) == 1:
            end = list(g.objects(rdflib.term.URIRef(self.uri), rdfEnd))
            duration = list(g.objects(rdflib.term.URIRef(self.uri), settings.NS.vcal.duration))
            start = start[0].toPython()
            if len(end) == 1:
                occur, created = m.objects.get_or_create(start_time=start, end_time=end[0].toPython(), event=self)
            elif len(duration) == 1:
                end = start + duration[0].toPython()
                occur, created = m.objects.get_or_create(start_time=start, end_time=end, event=self)
        elif len(start) == 0:
            # Il faut chercher les uri de la forme self.uri#i avec i = 1,2,3,....
            i = 0
            again = True
            while again:
                i += 1
                uri = self.uri + "#%s" % i
                start = list(g.objects(rdflib.term.URIRef(uri), rdfStart))
                again = not start == []
                if len(start) == 1:
                    end = list(g.objects(rdflib.term.URIRef(uri), rdfEnd))
                    duration = list(g.objects(rdflib.term.URIRef(uri), settings.NS.vcal.duration))
                    start = start[0].toPython()
                    if len(end) == 1:
                        occur, created = m.objects.get_or_create(start_time=start, end_time=end[0].toPython(), event=self)
                    elif len(duration) == 1:
                        end = start + duration[0].toPython()
                        occur, created = m.objects.get_or_create(start_time=start, end_time=end, event=self)
                else:
                    pass
        else:
            pass


class BaseDated(models.Model):
    # things which are linked to an event
    event = models.ForeignKey('coop_local.Event', null=True, blank=True,
                                 verbose_name=_(u"event"))
    # generic key to other objects
    content_type = models.ForeignKey(ContentType, blank=True, null=True, default=None)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return unicode(self.content_object) + u" @ " + unicode(self.event)

    class Meta:
        abstract = True
        verbose_name = _(u'Dated item')
        verbose_name_plural = _(u'Dated items')
        app_label = 'coop_local'


class OccurrenceManager(models.Manager):
    use_for_related_fields = True

    def daily_occurrences(self, dt=None, event=None):
        """
        Returns a queryset of for instances that have any overlap with a
        particular day.

        * ``dt`` may be either a datetime.datetime, datetime.date object, or
          ``None``. If ``None``, default to the current day.

        * ``event`` can be an ``Event`` instance for further filtering.
        """
        dt = dt or datetime.now()
        start = datetime(dt.year, dt.month, dt.day)
        end = start.replace(hour=23, minute=59, second=59)
        qs = self.filter(
            models.Q(
                start_time__gte=start,
                start_time__lte=end,
            ) |
            models.Q(
                end_time__gte=start,
                end_time__lte=end,
            ) |
            models.Q(
                start_time__lt=start,
                end_time__gt=end
            )
        )
        if event:
            return qs.filter(event=event)
        else:
            return qs


class BaseOccurrence(models.Model):
    """
    Represents the start end time for a specific occurrence of a master ``Event``
    object.
    """
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    event = models.ForeignKey('coop_local.Event', verbose_name=_('event'), editable=False)

    objects = OccurrenceManager()

    class Meta:
        verbose_name = _('occurrence')
        verbose_name_plural = _('occurrences')
        ordering = ('start_time', 'end_time')
        abstract = True
        app_label = 'coop_local'

    def __unicode__(self):
        return _date(self.start_time, _("l j F Y"))

    @models.permalink
    def get_absolute_url(self):
        return ('agenda-occurrence', [str(self.event.id), str(self.id)])

    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)

    @property
    def title(self):
        return self.event.title

    @property
    def event_type(self):
        return self.event.event_type


def create_event(title, event_type, description='', start_time=None,
        end_time=None, note=None, **rrule_params):
    """
    Convenience function to create an ``Event``, optionally create an
    ``EventCategory``, and associated ``Occurrence``s. ``Occurrence`` creation
    rules match those for ``Event.add_occurrences``.

    Returns the newly created ``Event`` instance.

    Parameters

    ``event_type``
        can be either an ``EventCategory`` object or 2-tuple of ``(abbreviation,label)``,
        from which an ``EventCategory`` is either created or retrieved.

    ``start_time``
        will default to the current hour if ``None``

    ``end_time``
        will default to ``start_time`` plus agenda_settings.DEFAULT_OCCURRENCE_DURATION
        hour if ``None``

    ``freq``, ``count``, ``rrule_params``
        follow the ``dateutils`` API (see http://labix.org/python-dateutil)
    """
    from coop.agenda.conf import settings as agenda_settings

    if isinstance(event_type, tuple):
        event_type, created = get_model('coop_local', 'EventCategory').objects.get_or_create(
            abbr=event_type[0],
        )
        if created:
            event_type.label = event_type[1]
            event_type.save()

    event = get_model('coop_local', 'Event').objects.create(
        title=title,
        description=description,
        event_type=event_type
    )

    start_time = start_time or datetime.now().replace(
        minute=0,
        second=0,
        microsecond=0
    )

    end_time = end_time or start_time + agenda_settings.DEFAULT_OCCURRENCE_DURATION
    event.add_occurrences(start_time, end_time, **rrule_params)
    return event
