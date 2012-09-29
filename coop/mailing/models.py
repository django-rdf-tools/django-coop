# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from extended_choices import Choices
from django.core.exceptions import ValidationError
from coop.mailing import soap
from django.contrib.sites.models import Site
from django.conf import settings


# The sympa templates for list
# /home/sympa/default/create_list_template
# they MUST match the repositories name, this is the aim of the
# templateName property
DISPLAY = Choices(
    ('DISCUSSION_LIST', 1, _(u'discussion list')),
    ('HOSTLINE',   2,  _(u'hotline')),
    ('HTML_NEWS_LETTER',  3,  _(u'html news letter')),
    ('INTRANET_LIST', 4,  _(u'intranet list')),
    ('NEWS_LETTER', 5,  _(u'news letter')),
    ('PRIVATE_WORKING',     6,  _(u'private working')),
    ('PUBLIC_WEB_FORUM',   7,  _(u'public web forum')),
    ('NEWS_REMOTE_SOURCE', 8, _(u'diffusion list with remote source')),
)


class BaseMailingList(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)
    email = models.EmailField(_('Newsletter email'), editable=False)
    # main_url = models.URLField(_('List URL'))

    # Specific field to run sympa
    subject = models.CharField(max_length=200)
    template = models.PositiveSmallIntegerField(_(u'template'),
                    choices=DISPLAY.CHOICES, default=DISPLAY.NEWS_REMOTE_SOURCE)
    description = models.TextField(blank=True)  # could contains html balises
    # A choisir dans une liste... qui parametre cette liste,est-t-elle modifiable?
    # ... et encore pleins de questions. C'est de la mecanique interne a sympa et cela
    # semble optionnel.... on peut peut etre s'en passer et le gerer par nos tags
    # topics = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u"%s" % self.name

    # laliste sympa est deja cree
    def clean(self, *args, **kwargs):
        # TODO quant on aura ajouter les noms de domaines... il faudrait
        # surement modifier des choses
        if soap.exists(self.name):
            raise ValidationError(_(u"List %s exists. If you want to reopen it, please contact the sympa list administator" % self.name))
        if not self.email:
            self.email = "%s@%s" % (self.name, Site.objects.get_current())
        if self.template == 8:
            # subject = '%s%shttp://%s/sympa_remote_list/%s' % (self.subject, settings.SYMPA_SOAP['PARAMETER_SEPARATOR'], Site.objects.get_current(), self.name)
            subject = '%s%shttp://www.credis.org/tmp/test_list.txt' % (self.subject, settings.SYMPA_SOAP['PARAMETER_SEPARATOR'])
        else:
            subject = self.subject
        result = soap.create_list(self.name, subject, self.templateName, self.description)
        if not result == 1:
            raise ValidationError(_(u"Cannot add the list (sympa cannot create it): %s" % result))
        super(BaseMailingList, self).clean(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        return self.clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(BaseMailingList, self).save(*args, **kwargs)

    def delete(self):
        result = 1
        if soap.exists(self.name):
            result = soap.close_list(self.name)

        if result == 1 or result == 'list allready closed':
            super(BaseMailingList, self).delete()
        else:
            raise Exception(_(u"Cannot close the list : %s" % result))


    class Meta:
        verbose_name = _('mailing list')
        verbose_name_plural = _('mailing lists')
        abstract = True
        app_label = 'coop_local'

    @property
    def templateName(self):
        """ We have to retourn the orresponding repertory name
        Please check with sympa server directory /home/sympa/default/create_list_templates
        """
        if self.template == DISPLAY.DISCUSSION_LIST:
            return 'discussion_list'
        elif self.template == DISPLAY.HOSTLINE:
            return 'hotline'
        elif self.template == DISPLAY.HTML_NEWS_LETTER:
            return 'html-news-letter'
        elif self.template == DISPLAY.INTRANET_LIST:
            return 'intranet_list'
        elif self.template == DISPLAY.NEWS_LETTER:
            return 'news-letter'
        elif self.template == DISPLAY.PRIVATE_WORKING:
            return 'private_working_group'
        elif self.template == DISPLAY.PUBLIC_WEB_FORUM:
            return 'pulic_web_forum'
        elif self.template == DISPLAY.NEWS_REMOTE_SOURCE:
            return 'news-remote-source'
        else:
            return ''


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
