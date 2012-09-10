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


class BaseCalendar(models.Model):
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
        return reverse('agenda-calendar', args=[self.slug])


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


class BaseEvent(URIModel):
    """
    Container model for general metadata and associated ``Occurrence`` entries.
    """
    title = models.CharField(_('title'), max_length=32)
    description = models.TextField(_(u'description'), blank=True)
    slug = exfields.AutoSlugField(populate_from='title')
    event_type = models.ForeignKey('coop_local.EventCategory', verbose_name=_('event type'))
    calendar = models.ForeignKey('coop_local.Calendar', verbose_name=_('calendar'))

    # Linking to local objects
    organization = models.ForeignKey('coop_local.Organization', null=True, blank=True, verbose_name=_('organization'))
    person = models.ForeignKey('coop_local.Person', null=True, blank=True, verbose_name=_('author'))

    # Linking to remote objects
    remote_person_uri = models.CharField(_('author URI'), blank=True, max_length=255, editable=False)
    remote_person_label = models.CharField(_(u'external author'),
                                                max_length=250, blank=True, null=True,
                                                help_text=_(u'fill this only if the person record is not available locally'))
    remote_organization_uri = models.CharField(_('organization URI'), blank=True, max_length=255, editable=False)
    remote_organization_label = models.CharField(_(u'external organization'),
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
        return u'%s: %s' % (self.title, self.start_time.isoformat())

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
