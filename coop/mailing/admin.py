# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.forms import ValidationError
from coop_local.models import NewsletterSending, Subscription, Newsletter, MailingList
from coop_local.models import Article, Event
from django.db.models.loading import get_model
from django import forms
try:
    from chosen.widgets import ChosenSelectMultiple
except ImportError:
    # print "chosen missing"
    pass
from coop.mailing.forms import get_newsletter_templates
from coop.mailing import soap


class SubscriptionInline(admin.TabularInline):
    #model = get_model('coop_local', 'Subscription')
    model = Subscription
    fk_name = 'mailing_list'
    verbose_name = _(u'subscription')
    verbose_name_plural = _(u'subscriptions')
    #content_type_whitelist = ('coop_local/person', 'coop_local/organization')
    #fields = ('modified',)
    extra = 1


class MailingListInline(admin.TabularInline):
    model = get_model('coop_local', 'MailingList')
    verbose_name = _(u'mailing list')
    verbose_name_plural = _(u'mailing list')
    fields = ('name', 'subject', 'description')
    readonly_fields = ('email',)
    extra = 1




class ReverseRelationshipInlineForm(forms.ModelForm):
    class Meta:
        model = Subscription


class ReverseRelationshipInline(admin.TabularInline):
    model = Subscription
    form = ReverseRelationshipInlineForm
    fields = ('link_content_object',)
    readonly_fields = ('link_content_object',)
    extra = 1



class MailingListAdminForm(forms.ModelForm):

    def clean_description(self):
        desc = self.cleaned_data['description']
        if desc == '':
            return self.data['name']
        else:
            return desc

    def clean_name(self):
        name = self.cleaned_data['name']
        if soap.exists(name):
            # Update subscription options
            if MailingList.objects.filter(name=name).exists():
                return name
            # sympa mailing list has been closed
            else:
                raise ValidationError(_(u" list exits already on sympa server, please contact Sympa administrateur"))
        else:
            return name


    class Meta:
        model = get_model('coop_local', 'MailingList')


class MailingListAdmin(admin.ModelAdmin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    # list_display_links = ['email', ]
    form = MailingListAdminForm
    search_fields = ['name', 'subject', 'email', 'description']
    list_per_page = 10
    list_select_related = True
    read_only_fields = ['created', 'modified']
    ordering = ('name',)
    readonly_fields = ('email',)

    inlines = [ReverseRelationshipInline]

    fieldsets = (
        ('Description', {
            'fields': ['name',
                       'subject',
                       'template',
                       'description',
                       'email',
                        ('subscription_option', 'subscription_filter_with_tags'),
                        'person_category', 'organization_category',
                       'tags'
                       ]
            }),
    )

    # To exlucde de 'fake' MailingList as writen
    def queryset(self, request):
        qs = super(MailingListAdmin, self).queryset(request)
        return qs.exclude(name='fake')



class NewsletterSendingInline(admin.StackedInline):
    #form = SingleOccurrenceForm
    verbose_name = _(u'Sending Date')
    verbose_name_plural = _(u'Sending Dates')
    model = NewsletterSending
    readonly_fields = ('sending_dt',)

    extra = 1



class NewsletterAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NewsletterAdminForm, self).__init__(*args, **kwargs)
        self.newsletter = kwargs.get('instance', None)
        choices = get_newsletter_templates(self.newsletter)
        if choices:
            self.fields["template"] = forms.ChoiceField(choices=choices)
        else:
            self.fields["template"] = forms.CharField()

        self.fields['lists'].queryset = MailingList.objects.exclude(name='fake')
        self.fields['articles'].queryset = Article.objects.all().order_by('-modified')
        self.fields['events'].queryset = Event.objects.all().order_by('-modified')
        # self.fields['articles'].widget = admin.widgets.FilteredSelectMultiple(
        #      _(u'Articles'), True,)

    class Meta:
        model = Newsletter
        widgets = {}
        try:
            widgets.update({
                'items': ChosenSelectMultiple(),
            })
        except NameError:
            # print 'No ChosenSelectMultiple'
            pass

    class Media:
        css = {
            'all': ('css/admin-tricks.css',),
        }
        js = ()


class NewsletterAdmin(admin.ModelAdmin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    form = NewsletterAdminForm
    inlines = [NewsletterSendingInline]
    fieldsets = (
        ('Description', {
            'fields': ['subject',
                       'content',
                       'template',
                       'articles', 'events',
                       'lists'
                       ]
            }),
        )


