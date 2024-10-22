# -*- coding:utf-8 -*-
from django.db import models
from django.forms import ValidationError
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from extended_choices import Choices
from coop.mailing import soap
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.urlresolvers import reverse
import logging
from django.core import urlresolvers
from django.contrib.auth.models import User
from django.db.models.loading import get_model

log = logging.getLogger('coop')

#####################################################
#
#  Mailling List
#
#####################################################



# The sympa templates for list
# /home/sympa/default/create_list_template
# they MUST match the repositories name, this is the aim of the
# sympa_template_name property

SYMPA_TEMPLATES = Choices(
    ('DISCUSSION_LIST', 1, _(u'discussion list')),
    ('HOSTLINE',   2,  _(u'hotline')),
    ('HTML_NEWS_LETTER',  3,  _(u'html news letter')),
    ('INTRANET_LIST', 4,  _(u'intranet list')),
    ('NEWS_LETTER', 5,  _(u'news letter')),
    ('PRIVATE_WORKING',     6,  _(u'private working')),
    ('PUBLIC_WEB_FORUM',   7,  _(u'public web forum')),
)

SUBSCRIPTION_OPTION = Choices(
    ('MANUAL', 1, _(u'manual choice')),
    ('ALL', 2, _(u'persons and organizations')),
    ('ALL_ORGS', 3, _(u'organizations only')),
    ('ALL_PERSONS', 4, _(u'persons only')),
    # ('ORGS_OPTION', 5, _(u'some organization contacts')),
)


class BaseMailingList(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)
    # various subscription option
    subscription_option = models.PositiveSmallIntegerField(_(u'email choice'),
                    choices=SUBSCRIPTION_OPTION.CHOICES, default=SUBSCRIPTION_OPTION.ALL,
                    help_text=_(u'Manual > other option = losing selection!'))
    subscription_filter_with_tags = models.BooleanField(_(u'filter subscriptions with tags'), default=False)
    person_category = models.ForeignKey('coop_local.PersonCategory',
                                         verbose_name=_('person category'), 
                                         blank=True, null=True)
    organization_category = models.ForeignKey('coop_local.OrganizationCategory', 
                                                verbose_name=_('organization category'), 
                                                blank=True, null=True)
    description = models.TextField(_(u'description'), blank=True, null=True)  # can contain html markup


    # Specific fields for sympa
    email = models.EmailField(_('Mailing list email'), editable=False)
    subject = exfields.AutoSlugField(_(u'intitulé'), populate_from=('name'), overwrite=True)
    # avec ce templateon peut gerer les inscripts depuis django-coop. Sinon.... passer par sympa
    template = models.PositiveSmallIntegerField(_(u'template'),
                    choices=SYMPA_TEMPLATES.CHOICES, default=SYMPA_TEMPLATES.NEWS_LETTER)

    def __unicode__(self):
        return self.name

    def count_display(self):
        nb = self.subs.count()
        return str(nb) + ' destinataires'
    count_display.allow_tags = True
    count_display.short_description = u'Taille'

    def mode_display(self):
        return SUBSCRIPTION_OPTION.CHOICES_DICT[self.subscription_option]
    mode_display.allow_tags = True
    mode_display.short_description = u'mode'


    #  attention code lié à l'existence d'un serveur SYMPA avec un FQDN genre listes.truc.com
    def build_email(self):
        domain = '.'.join(Site.objects.get_current().domain.split('.')[1:])
        return "%s@listes.%s" % (self.name, domain)

    # This is not really a QuerySet,as we want to use the similar_objects property from tags
    def person_qs(self):
        from coop_local.models import Person
        res = Person.objects.none()
        if self.subscription_option in [SUBSCRIPTION_OPTION.ALL, SUBSCRIPTION_OPTION.ALL_PERSONS]:
            if self.person_category:
                res = Person.objects.filter(category__in=[self.person_category], mailing=True)
            else:
                res = Person.objects.filter(mailing=True)

            if self.organization_category:
                orgs_in_cat = get_model('coop_local', 'Organization').objects.filter(category=self.organization_category)
                res = res.filter(organization__in=orgs_in_cat)

        res = set(res)
        if not self.subscription_filter_with_tags:
            return res
        elif self.pk:
            similar_objects = set(self.tags.similar_objects())
            # the intersection
            return res.intersection(similar_objects)
        else:
            return res

    def org_qs(self):
        from coop_local.models import Organization
        res = Organization.objects.none()
        if self.subscription_option in [SUBSCRIPTION_OPTION.ALL, SUBSCRIPTION_OPTION.ALL_ORGS]:
            if self.organization_category:
                res = Organization.objects.filter(category__in=[self.organization_category])
            else:
                res = Organization.objects.all()
        res = set(res)
        if not self.subscription_filter_with_tags:
            return res
        elif self.pk:
            similar_objects = set(self.tags.similar_objects())
            # the intersection
            return res.intersection(similar_objects)
        else:
            return res

    def build_sympa_subject(self):
        # We choosed to include meta-information about the list inside the subject when
        # passing the SOAP command. This is then catched up by the templating system of SYMPA.
        sep = settings.SYMPA_SOAP['PARAMETER_SEPARATOR']
        remote_list_addr = 'http://%s/sympa_remote_list/%s/' % (Site.objects.get_current().domain, self.name)
        user = settings.SYMPA_SOAP['SYMPA_TMPL_USER']
        passwd = settings.SYMPA_SOAP['SYMPA_TMPL_PASSWD']
        return sep.join([self.subject, remote_list_addr, user, passwd])

    def save(self, *args, **kwargs):
        # self.full_clean()
        if self.id is None and soap.sympa_available():
            if not soap.exists(self.name):
                result = soap.create_list(self.name,
                                          self.build_sympa_subject(),
                                          self.sympa_template_name,
                                          self.description
                                          )
                if not result == 1:
                    raise ValidationError(_(u"Cannot add the list (sympa cannot create it): %s" % result))
            else:
                raise ValidationError(_(u'list already exists on sympa server, please contact Sympa administrator'))
            self.email = soap.info(self.name).listAddress

        super(BaseMailingList, self).save(*args, **kwargs)
        self.verify_subscriptions(delete=False)

    def delete(self):
        result = 1
        if soap.exists(self.name):
            result = soap.close_list(self.name)

        if result == 1 or result == 'list already closed':
            super(BaseMailingList, self).delete()
        else:
            raise Exception(_(u"Cannot close the list : %s" % result))

    class Meta:
        verbose_name = _(u'mailing list')
        verbose_name_plural = _(u'mailing lists')
        abstract = True
        app_label = 'coop_local'

    @property
    def sympa_template_name(self):
        """ We have to retourn the corresponding repertory name
        Please check with sympa server directory /home/sympa/default/create_list_templates
        """
        if self.template == SYMPA_TEMPLATES.DISCUSSION_LIST:
            return 'discussion_list-remote-source'
        elif self.template == SYMPA_TEMPLATES.HOSTLINE:
            return 'hotline-remote-source'
        elif self.template == SYMPA_TEMPLATES.HTML_NEWS_LETTER:
            return 'html-news-letter-remote-source'
        elif self.template == SYMPA_TEMPLATES.INTRANET_LIST:
            return 'intranet_list-remote-source'
        elif self.template == SYMPA_TEMPLATES.NEWS_LETTER:
            return 'news-letter-remote-source'
        elif self.template == SYMPA_TEMPLATES.PRIVATE_WORKING:
            return 'private_working_group-remote-source'
        elif self.template == SYMPA_TEMPLATES.PUBLIC_WEB_FORUM:
            return 'public_web_forum-remote-source'
        else:
            # let's create the list. This one is moderated...
            return 'news-letter-remote-source'

    def _instance_to_subscription(self, instance):
        from coop_local.models import Subscription
        if instance.pref_email and instance.mailing: 
            # ct will tell us if we're about to subscribe a person or an organization
            ct = ContentType.objects.get_for_model(instance)
            qs = Subscription.objects.filter(mailing_list=self,
                                             content_type__pk=ct.id,
                                             object_id=instance.id)
            if not qs.exists():
                subs = Subscription(mailing_list=self, content_object=instance)
                subs.save()

    def auto_subscription(self):
        for person in self.person_qs():
            self._instance_to_subscription(person)

        for org in self.org_qs():
            self._instance_to_subscription(org)

    # The 'delete' parameter is a workaround to avoid deleting subscription
    # as the mailinglist is updated with the admin interface. Django bug, missunderstanding???
    def verify_subscriptions(self, delete=True):
        from coop_local.models import Subscription, MailingList
        # Cleaning....
        # if delete:
        #     fake = MailingList.objects.get(name='fake')
        #     for s in Subscription.objects.filter(mailing_list=fake):
        #         s.delete()
        
        if not self.subscription_option == SUBSCRIPTION_OPTION.MANUAL:
            orgs = ContentType.objects.get(app_label='coop_local', model='organization')
            pers = ContentType.objects.get(app_label='coop_local', model='person')
            orgs_ids = set(self.subs.filter(content_type=orgs).values_list('object_id', flat=True))
            pers_ids = set(self.subs.filter(content_type=pers).values_list('object_id', flat=True))

            orgs_subscribed = set(map(lambda x: orgs.get_object_for_this_type(pk=x), orgs_ids))
            pers_subscribed = set(map(lambda x: pers.get_object_for_this_type(pk=x), pers_ids))
            orgs_to_be_subscribed = set(self.org_qs())
            pers_to_be_subscribed = set(self.person_qs())

            print '%d organizations subscribed' % len(orgs_subscribed)
            print '%d organizations to be subscribed' % len(orgs_to_be_subscribed)
            print '%d persons subscribed' % len(pers_subscribed)
            print '%d persons to be subscribed' % len(pers_to_be_subscribed)

            # import ipdb; ipdb.set_trace()

            # The news subscriptions
            for org in orgs_to_be_subscribed.difference(orgs_subscribed):
                self._instance_to_subscription(org)
            for person in pers_to_be_subscribed.difference(pers_subscribed):
                self._instance_to_subscription(person)
            # and some have to be deleted
            for org in orgs_subscribed.difference(orgs_to_be_subscribed):
                try:
                    sub = Subscription.objects.get(mailing_list=self, content_type=orgs, object_id=org.id)
                    # if delete:
                    sub.delete()    # We can NOT delete... pb with formset and admin!!!!
                    # else:
                    #     subs.mailing_list = MailingList.objects.get(name='fake')
                    #     subs.save()
                except Subscription.DoesNotExist:
                    print 'strange ...can not find Orgs %s' % org.id
            for person in pers_subscribed.difference(pers_to_be_subscribed):
                try:
                    subs = Subscription.objects.get(mailing_list=self, content_type=pers, object_id=person.id)
                    # if delete:
                    subs.delete()
                    # else:
                    #     subs.mailing_list = MailingList.objects.get(name='fake')
                    #     subs.save()
                except Subscription.DoesNotExist:
                    print 'strange ....can not find %s Person' % person.id

            # TO TEST
        else :
            subs = Subscription.objects.filter(mailing_list=self)
            for s in subs:
                if not s.content_object.pref_email or not s.content_object.pref_email.content:
                    s.delete()


    def sympa_export_list(self):
        from coop_local.models import Subscription
        self.verify_subscriptions()
        res = ''
        for s in Subscription.objects.filter(mailing_list=self):
            email = s.content_object.pref_email.content
            label = s.content_object.label()
            if label:
                res += '%s %s\n' % (email, label)
            else:
                res += '%s\n' % email
        return res

    def dest_dicts(self):
        from coop_local.models import Subscription
        self.verify_subscriptions()
        res = []
        for s in Subscription.objects.filter(mailing_list=self):
            res.append({'email': s.content_object.pref_email.content,
                        'name': s.content_object.label(),
                        'uuid': s.content_object.uuid
                        })
        return res

# def on_create_mailing_instance(sender, instance, created, raw, **kwargs):
#     from coop_local.models import MailingList
#     if sender == MailingList:
#         if not instance.subscription_option == SUBSCRIPTION_OPTION.MANUAL:
#             instance.verify_subscriptions()
# post_save.connect(on_create_mailing_instance)



class BaseSubscription(models.Model):
    mailing_list = models.ForeignKey('coop_local.MailingList',
                                        related_name='subs')
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)
    # label = models.CharField(max_length=250, null=True)
    # subscription options (HTML, text ...)
    # email = models.EmailField(_('subscribed email'), default='')

    # things which are suscribed
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('mailing list subscription')
        verbose_name_plural = _('mailing list subscriptions')
        abstract = True
        app_label = 'coop_local'
        # ordering = ['pref_email']

    def __unicode__(self):
        return '%s (%s)' % (unicode(self.content_object.pref_email), self.content_object.label())

    def link_content_object(self):
        obj = self.content_object
        change_url = urlresolvers.reverse(
            'admin:%s_%s_change' % (
                obj._meta.app_label,
                obj._meta.object_name.lower()
            ),
            args=(obj.id,)
        )
        return u'<a href="%s">%s</a>' % (change_url,  obj.__unicode__())
    link_content_object.allow_tags = True
    link_content_object.short_description = u'abonné'



#####################################################
#
#  Newsletter
#
#####################################################


class BaseNewsletter(models.Model):
    subject = models.CharField(max_length=200, verbose_name=_(u'subject'), blank=True, default="")
    content = models.TextField(_(u"summary"), default="<br>", blank=True)
    # items = models.ManyToManyField('coop_local.NewsletterItem', blank=True)

    template = models.CharField(_(u'template'), max_length=200, default='mailing/newsletter.html', blank=True)

    # articles = models.ManyToManyField('coop_local.Article', null=True, blank=True)
    # events = models.ManyToManyField('coop_local.Event', null=True, blank=True)

    lists = models.ManyToManyField('coop_local.MailingList', verbose_name=_(u'destination lists'), blank=True, null=True)

    def get_items(self):
        return None
        # return [item.content_object for item in self.items.all()]

    def get_items_by_category(self):
        return None
        # items = self.get_items()

        # def sort_by_category(item):
        #     category = getattr(item, 'category', None)
        #     if category:
        #         return category.ordering
        #     return 0
        # items.sort(key=sort_by_category)
        # return items

    @property
    def articles(self):
        ct = ContentType.objects.get(app_label='coop_local', model='article')
        return ct.model_class().objects.filter(id__in=
            self.elements.filter(content_type=ct).values_list('object_id', flat=True))

    @property
    def resources(self):
        ct = ContentType.objects.get(app_label='coop_local', model='docresource')
        return ct.model_class().objects.filter(id__in=
            self.elements.filter(content_type=ct).values_list('object_id', flat=True))

    @property
    def organizations(self):
        ct = ContentType.objects.get(app_label='coop_local', model='organization')
        return ct.model_class().objects.filter(id__in=
            self.elements.filter(content_type=ct).values_list('object_id', flat=True))

    @property
    def projects(self):
        ct = ContentType.objects.get(app_label='coop_local', model='project')
        return ct.model_class().objects.filter(id__in=
            self.elements.filter(content_type=ct).values_list('object_id', flat=True))

    @property
    def exchanges(self):
        ct = ContentType.objects.get(app_label='coop_local', model='exchange')
        return ct.model_class().objects.filter(id__in=
            self.elements.filter(content_type=ct).values_list('object_id', flat=True))


    def can_edit_newsletter(self, user):
        return user.has_perm('coop.mailing.change_newsletter')

    def get_absolute_url(self):
        return reverse('coop_view_newsletter', args=[self.id])

    def get_edit_url(self):
        return reverse('coop_edit_newsletter', args=[self.id])

    def get_template_name(self):
        template = self.template
        if not template:
            self = 'mailing/newsletter.html'
        return template

    def __unicode__(self):
        return self.subject

    class Meta:
        abstract = True
        app_label = 'coop_local'
        verbose_name = _(u'newsletter')
        verbose_name_plural = _(u'newsletters')


class BaseNewsElement(models.Model):
    newsletter = models.ForeignKey('coop_local.Newsletter', related_name='elements')
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True
        app_label = 'coop_local'
        # unique_together = ("newsletter", "content_type", "object_id")

    def __unicode__(self):
        return u'%s -> %s' % (self.content_object.__unicode__(), self.newsletter.subject)



class BaseNewsletterSending(models.Model):

    newsletter = models.ForeignKey('coop_local.Newsletter')
    scheduling_dt = models.DateTimeField(_(u"scheduling date"), blank=True, default=None, null=True)
    sending_dt = models.DateTimeField(_(u"sending date"), blank=True, default=None, null=True, editable=False)

    def __unicode__(self):
        return self.newsletter.subject

    class Meta:
        verbose_name = _(u'newsletter sending')
        verbose_name_plural = _(u'newsletter sendings')
        abstract = True
        app_label = 'coop_local'


def instance_to_pref_email(instance):
    if hasattr(instance, 'pref_email') and instance.pref_email:
        return instance.pref_email.content


# class NewsletterMixin(models.Model):
#     # tags = generic.GenericRelation(TaggedItem)
#     newsletter = models.ForeignKey('coop_local.Newsletter', verbose_name=u'newsletter',
#                                 blank=True, null=True, related_name='newsletter_objects')

#     class Meta:
#         abstract = True
#         app_label = 'coop_local'





