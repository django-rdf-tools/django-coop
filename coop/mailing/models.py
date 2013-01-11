# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from extended_choices import Choices
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from coop.mailing import soap
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save, pre_delete
from coop.org.models import COMM_MEANS, DISPLAY
import logging

log = logging.getLogger('coop')

#####################################################
#
#  Mailling List
#
#####################################################



# The sympa templates for list
# /home/sympa/default/create_list_template
# they MUST match the repositories name, this is the aim of the
# templateName property
SYMPA_TEMPLATES = Choices(
    ('DISCUSSION_LIST', 1, _(u'discussion list')),
    ('HOSTLINE',   2,  _(u'hotline')),
    ('HTML_NEWS_LETTER',  3,  _(u'html news letter')),
    ('INTRANET_LIST', 4,  _(u'intranet list')),
    ('NEWS_LETTER', 5,  _(u'news letter')),
    ('PRIVATE_WORKING',     6,  _(u'private working')),
    ('PUBLIC_WEB_FORUM',   7,  _(u'public web forum')),
    ('NEWS_REMOTE_SOURCE', 8, _(u'news letter list with remote source')),
)

SUBSCRIPTION_OPTION = Choices(
    ('MANUAL', 1, _(u'custom email list')),
    ('ALL', 2, _(u'all email address')),
    ('ALL_ORGS', 3, _(u'all organizations contact')),
    ('ALL_PERSONS', 4, _(u'all registered persons')),
    # ('ORGS_OPTION', 5, _(u'some organization contacts')),    
)


class BaseMailingList(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)
    # The 'slug' field is used to build the email of the list
    slug = exfields.AutoSlugField(populate_from=('name'), overwrite=True, editable=False)
    # pour le moment, le champs suivant sert uniquement pour info
    email = models.EmailField(_('Mailing list email'), editable=False)

    # various subscription option
    subscription_option = models.PositiveSmallIntegerField(_(u'subscriptions option'),
                    choices=SUBSCRIPTION_OPTION.CHOICES, default=SUBSCRIPTION_OPTION.MANUAL)
    subscription_filter_with_tags = models.BooleanField(_(u'filter subscriptions with tags'), default=False)

    person_category = models.ForeignKey('coop_local.Person', verbose_name=_('person category'), blank=True, null=True)
    organization_category = models.ForeignKey('coop_local.Organization', verbose_name=_('organization category'), blank=True, null=True)

    # Specific field to run sympa
    subject = models.CharField(max_length=200)
    # avec ce templateon peut gerer les inscripts depuis django-coop. Sinon.... passer par sympa
    template = models.PositiveSmallIntegerField(_(u'template'),
                    choices=SYMPA_TEMPLATES.CHOICES, default=SYMPA_TEMPLATES.NEWS_REMOTE_SOURCE)
    description = models.TextField(blank=True)  # could contains html balises
    # A choisir dans une liste... qui parametre cette liste,est-t-elle modifiable?
    # ... et encore pleins de questions. C'est de la mecanique interne a sympa et cela
    # semble optionnel.... on peut peut etre s'en passer et le gerer par nos tags
    # topics = models.CharField(max_length=200, blank=True)


    # def __str__(self):
    #     return self.name

    def __unicode__(self):
        return u"%s: %s" % (self.name, self.subject)

    #  attention ce code est vraiment lié a notre sysem de mailing list
    def build_email(self):
        domain = '.'.join(Site.objects.get_current().domain.split('.')[1:])
        return "%s@listes.%s" % (self.slug, domain)

    # laliste sympa est deja cree
    def clean(self, *args, **kwargs):
        if soap.sympa_available():
            if soap.exists(self.slug):
                raise ValidationError(_(u"List %s exists. If you want to reopen it, please contact the sympa list administator" % self.slug))
            if not self.email:
                self.email = self.build_email()
            if self.template == 8:
                # subject = '%s%shttp://%s/sympa_remote_list/%s' % (self.subject, settings.SYMPA_SOAP['PARAMETER_SEPARATOR'], Site.objects.get_current(), self.name)
                subject = '%s%shttp://%s%s' % \
                    (self.subject, 
                     settings.SYMPA_SOAP['PARAMETER_SEPARATOR'], 
                     Site.objects.get_current(),
                     reverse('sympa_remote_list', args=[self.id]))
            else:
                subject = self.subject
            result = soap.create_list(self.slug, subject, self.templateName, self.description)
            if not result == 1:
                raise ValidationError(_(u"Cannot add the list (sympa cannot create it): %s" % result))
        # let's build the mailing list even if soap server is not accessible
        super(BaseMailingList, self).clean(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        super(BaseMailingList, self).full_clean(*args, **kwargs)
        return self.clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self._meta.get_field('slug').pre_save(self, True)  # Slug have to be uptodate
        self.full_clean()
        super(BaseMailingList, self).save(*args, **kwargs)

    def delete(self):
        result = 1
        if soap.exists(self.slug):
            result = soap.close_list(self.slug)

        if result == 1 or result == 'list allready closed':
            super(BaseMailingList, self).delete()
        else:
            raise Exception(_(u"Cannot close the list : %s" % result))


    class Meta:
        verbose_name = _(u'mailing list')
        verbose_name_plural = _(u'mailing lists')
        abstract = True
        app_label = 'coop_local'

    @property
    def templateName(self):
        """ We have to retourn the corresponding repertory name
        Please check with sympa server directory /home/sympa/default/create_list_templates
        """
        if self.template == SYMPA_TEMPLATES.DISCUSSION_LIST:
            return 'discussion_list'
        elif self.template == SYMPA_TEMPLATES.HOSTLINE:
            return 'hotline'
        elif self.template == SYMPA_TEMPLATES.HTML_NEWS_LETTER:
            return 'html-news-letter'
        elif self.template == SYMPA_TEMPLATES.INTRANET_LIST:
            return 'intranet_list'
        elif self.template == SYMPA_TEMPLATES.NEWS_LETTER:
            return 'news-letter'
        elif self.template == SYMPA_TEMPLATES.PRIVATE_WORKING:
            return 'private_working_group'
        elif self.template == SYMPA_TEMPLATES.PUBLIC_WEB_FORUM:
            return 'pulic_web_forum'
        elif self.template == SYMPA_TEMPLATES.NEWS_REMOTE_SOURCE:
            return 'news-remote-source'
        else:
            return ''

    def _organization_to_subcription(self, org):
        from coop_local.models import Organization, Subscription

        if not 'ct_org' in self._organization_to_subcription.__dict__:
            self._organization_to_subcription.__dict__['ct_org'] = ContentType.objects.get_for_model(Organization)

        for org in Organization.objects.all():
            if org.pref_email and org.pref_email.display == DISPLAY.PUBLIC:
                # check for doublon
                qs = Subscription.objects.filter(mailing_list=self, email=org.pref_email.content)
                if qs.exists():
                    subs = qs[0]
                    subs.label = org.label()
                    subs.save()
                else:
                    Subscription.objects.get_or_create(email=org.pref_email.content, 
                                                    object_id=org.id,
                                                    mailing_list=self,
                                                    content_type=self._organization_to_subcription.__dict__['ct_org'], 
                                                    label=org.label())

    def _person_to_subscription(self, person):
        # cache stuff
        if not 'ct_person' in self._person_to_subscription.__dict__:
            from coop_local.models import Person
            self._person_to_subscription.__dict__['ct_person'] = ContentType.objects.get_for_model(Person)
 
        from coop_local.models import Subscription
        contacts = person.contact.filter(category=COMM_MEANS.MAIL)
        if contacts.exists():
            contacts = contacts.filter(display=DISPLAY.PUBLIC)
            if contacts.exists():
                contact = contacts[0]
                # check for doublon
                qs = Subscription.objects.filter(mailing_list=self, email=contact.content)
                if qs.exists():
                    subs = qs[0]
                    subs.label = person.label()
                    subs.save()
                else:
                    subs, created = Subscription.objects.get_or_create(email=contact.content, 
                                                                    object_id=person.id, 
                                                                    mailing_list=self,
                                                                    label=person.label(),
                                                                    content_type=self._person_to_subscription.__dict__['ct_person'])
        else:
            if person.email and not person.email == '':
                qs = Subscription.objects.filter(mailing_list=self, email=person.email)
                if qs.exists():
                    subs = qs[0]
                    subs.label = person.label()
                    subs.save()
                else:
                    subs, created = Subscription.objects.get_or_create(email=person.email, 
                                                object_id=person.id,
                                                mailing_list=self,
                                                content_type=self._person_to_subscription.__dict__['ct_person'], 
                                                label=person.label())


    # buils subscriptions accordinf to the subcription_option
    def auto_subscription(self):
        from coop_local.models import Contact, Organization, Person, Subscription
        if not self.subscription_filter_with_tags:
            if self.subscription_option == SUBSCRIPTION_OPTION.ALL:
                for contact in Contact.objects.filter(category=COMM_MEANS.MAIL).filter(display=DISPLAY.PUBLIC):
                    # check for doublon
                    qs = Subscription.objects.filter(mailing_list=self, email=contact.content)
                    if not qs.exists():
                        subs, create = Subscription.objects.get_or_create(email=contact.content, 
                                                                          mailing_list=self,
                                                                          label=contact.content_type.get_object_for_this_type(id=contact.object_id).label(),
                                                                          object_id=contact.object_id, 
                                                                          content_type=contact.content_type)
            elif self.subscription_option == SUBSCRIPTION_OPTION.ALL_ORGS:
                for org in Organization.objects.all():
                    self._organization_to_subcription(org)
            elif self.subscription_option == SUBSCRIPTION_OPTION.ALL_PERSONS:
                for person in Person.objects.all():
                    self._person_to_subscription(person)
            # elif self.subscription_option == SUBSCRIPTION_OPTION.ORGS_OPTION:
            #     for org in self.org_subscriptions.all():
            #         self._organization_to_subcription(org)
        else:
            similar_objects = self.tags.similar_objects()
            for obj in similar_objects:
                if isinstance(obj, Organization) and \
                        self.subscription_option in [SUBSCRIPTION_OPTION.ALL, SUBSCRIPTION_OPTION.ALL_ORGS]:
                    self._organization_to_subcription(obj)
                elif isinstance(obj, Person) and \
                        self.subscription_option in [SUBSCRIPTION_OPTION.ALL, SUBSCRIPTION_OPTION.ALL_PERSONS]:
                    self._person_to_subscription(obj)

    def verify_subscriptions(self):
        if not self.subscription_option == SUBSCRIPTION_OPTION.MANUAL:
            orgs = ContentType.objects.get(app_label='coop_local', model_name='organization')
            pers = ContentType.objects.get(app_label='coop_local', model_name='person')
            orgs_ids = set(self.subs.filter(content_type=orgs).values_list('id', flat=True).order_by('id'))
            pers_ids = setself.subs.filter(content_type=pers).values_list('id', flat=True).order_by('id')






    def subscription_list(self):
        from coop_local.models import Subscription
        res = ''
        for s in Subscription.objects.filter(mailing_list=self):
            if s.label:
                res += '%s <%s>;\n' % (s.label, s.email)
            else:
                res += '<%s>;\n' % s.email
        return res


def on_create_mailing_instance(sender, instance, created, raw, **kwargs):
    from coop_local.models import MailingList
    if sender == MailingList:
        if not instance.subscription_option == SUBSCRIPTION_OPTION.MANUAL:
            instance.auto_subscription()
post_save.connect(on_create_mailing_instance)



# class Parameter(models.Model):
#     list = models.ForeignKey('coop_local.MailingList')
#     value = models.CharField(max_length=200)

#     def __str__(self):
#         return self.value

#     def __unicode__(self):
#         return u"%s" % self.value






class BaseSubscription(models.Model):
    mailing_list = models.ForeignKey('coop_local.MailingList',
                                        related_name='subs')
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)
    label = models.CharField(max_length=250, null=True)
    # subscription options (HTML, text ...)
    email = models.EmailField(_('subscribed email'), default='')

    # things which are suscribed
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('mailing list subscription')
        verbose_name_plural = _('mailing list subscriptions')
        abstract = True
        app_label = 'coop_local'

    def __unicode__(self):
        return _(u'subscription to ') + unicode(self.mailing_list)








#####################################################
#
#  News Letter
#
#####################################################


# class BaseNewsletterItem(models.Model):
#     content_type = models.ForeignKey(
#         ContentType, 
#         verbose_name=_("content_type"),        
#         related_name="%(app_label)s_%(class)s_newsletter_items"
#     )
#     object_id = models.PositiveIntegerField(verbose_name=_("object id"))
#     content_object = generic.GenericForeignKey('content_type', 'object_id')

#     class Meta:
#         abstract = True
#         app_label = 'coop_local'
#         unique_together = (("content_type", "object_id"),)
#         verbose_name = _(u'newsletter item')
#         verbose_name_plural = _(u'newsletter items')

#     def __unicode__(self):
#         return u'{0}: {1}'.format(self.content_type, self.content_object)


class BaseNewsletter(models.Model):
    subject = models.CharField(max_length=200, verbose_name=_(u'subject'), blank=True, default="")
    content = models.TextField(_(u"content"), default="<br>", blank=True)
    # items = models.ManyToManyField('coop_local.NewsletterItem', blank=True)

    template = models.CharField(_(u'template'), max_length=200, default='mailing/newsletter.html', blank=True)

    articles = models.ManyToManyField('coop_local.Article')
    events = models.ManyToManyField('coop_local.Event')

    lists = models.ManyToManyField('coop_local.MailingList', verbose_name=_(u'destination lists'))

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


    def can_edit_newsletter(self, user):
        return user.has_perm('coop_cms.change_newsletter')

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



class BaseNewsletterSending(models.Model):

    newsletter = models.ForeignKey('coop_local.Newsletter')
    sending_dt = models.DateTimeField(_(u"sending date"), blank=True, default=None, null=True)

    def __unicode__(self):
        return self.newsletter.subject

    class Meta:
        verbose_name = _(u'newsletter sending')
        verbose_name_plural = _(u'newsletter sendings')
        abstract = True
        app_label = 'coop_local'

# TODO à virer

def instance_to_pref_email(instance):
    if hasattr(instance, 'pref_email'):
        if instance.pref_email.display == DISPLAY.PUBLIC:
            return instance.pref_email.content
    if hasattr(instance, 'contact'):
        contacts = instance.contact.filter(category=COMM_MEANS.MAIL)
        if contacts.exists():
            contacts = contacts.filter(display=DISPLAY.PUBLIC)
            if contacts.exists():
                return contacts[0].content
    if hasattr(instance, 'email'):
        return instance.email


def get_coop_local_newletters_item_class():
    if hasattr(get_coop_local_newletters_item_class, '_cache_class'):
        return getattr(get_coop_local_newletters_item_class, '_cache_class')
    else:
        klass = models.get_model('coop_local', 'newsletteritem')
        setattr(get_coop_local_newletters_item_class, '_cache_class', klass)
    return klass


def coop_newletter_items_classes():
    if hasattr(coop_newletter_items_classes, '_cache_class'):
        return getattr(coop_newletter_items_classes, '_cache_class')
    else:
        classes = []
        for c in settings.COOP_NEWLETTER_ITEM_CLASSES:
            classes.append(models.get_model('coop_local', c))
        setattr(coop_newletter_items_classes, '_cache_class', classes)
        return classes


#delete item when content object is deleted
def on_delete_newsletterable_item(sender, instance, **kwargs):
    if sender in coop_newletter_items_classes():
        if hasattr(instance, 'id'):
            try:
                ct = ContentType.objects.get_for_model(instance)
                klass = get_coop_local_newletters_item_class()
                item = klass.objects.get(content_type=ct, object_id=instance.id)
                item.delete()
            except (klass.DoesNotExist, ContentType.DoesNotExist):
                pass
pre_delete.connect(on_delete_newsletterable_item)


def create_newsletter_item(instance):
    ct = ContentType.objects.get_for_model(instance)
    klass = get_coop_local_newletters_item_class()
    if getattr(instance, 'in_newsletter', True):
        #Create a newsletter item automatically
        #An optional 'in_newsletter' field can skip the automatic creation if set to False
        return klass.objects.get_or_create(content_type=ct, object_id=instance.id)
    elif hasattr(instance, 'in_newsletter'):
        #If 'in_newsletter' field existe and is False
        #We delete the Item if exists
        try:
            item = klass.objects.get(content_type=ct, object_id=instance.id)
            item.delete()
            return None, True
        except klass.DoesNotExist:
            return None, False


#create automatically a newsletter item for every objects configured as newsletter_item
def on_create_newsletterable_instance(sender, instance, created, raw, **kwargs):
    if sender in coop_newletter_items_classes():
        create_newsletter_item(instance)
post_save.connect(on_create_newsletterable_instance)

