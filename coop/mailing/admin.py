# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.forms import ValidationError
from coop_local.models import NewsletterSending, Subscription, Newsletter, MailingList
# from coop_local.models import Article, Event
from django.db.models.loading import get_model
from django import forms
from tinymce.widgets import AdminTinyMCE
from chosen import widgets as chosenwidgets
from django.utils.safestring import mark_safe
from django.conf.urls.defaults import patterns, include, url
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

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
                raise ValidationError(_(u" list already exists on sympa server, please contact Sympa administrator"))
        else:
            return name

    # class Media:
    #     js = ('js/mailing.js',)

    class Meta:
        model = get_model('coop_local', 'MailingList')


class MailingListAdmin(admin.ModelAdmin):
    change_form_template = 'mailing/admin/tabbed_change_form.html'
    list_display = ( 'subject', 'mode_display', 'count_display')
    list_display_links = ['subject', ]
    form = MailingListAdminForm
    search_fields = ['name', 'subject', 'email', 'description']
    list_per_page = 10
    list_select_related = True
    read_only_fields = ['created', 'modified']
    ordering = ('name',)
    readonly_fields = ('email',)
    # inlines = [ReverseRelationshipInline]
    fieldsets = [
        ('Description', {
            'fields': ['name',
                       'description',
                        'subscription_option',
                        'person_category', 'organization_category',
                        'subscription_filter_with_tags',
                       'tags'
                       ]
            }),
        ('Sympa', {

            'fields': ['template', 'email']

            })
    ]

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
    content = forms.CharField(widget=AdminTinyMCE(attrs={'cols': 80, 'rows': 60}), required=False)
    def __init__(self, *args, **kwargs):
        super(NewsletterAdminForm, self).__init__(*args, **kwargs)
        self.newsletter = kwargs.get('instance', None)
        choices = get_newsletter_templates(self.newsletter)

        if choices:
            self.fields["template"] = forms.ChoiceField(choices=choices)
        else:
            self.fields["template"] = forms.CharField()
        # if 'sites' in self.fields:
        #     self.fields['sites'].help_text = None
        # self.fields['lists'].queryset = MailingList.objects.exclude(name='fake')
        self.fields['lists'].help_text = None

        # self.fields['articles'].queryset = Article.objects.all().order_by('-modified')
        # self.fields['events'].queryset = Event.objects.all().order_by('-modified')
        # self.fields['articles'].widget = admin.widgets.FilteredSelectMultiple(
        #      _(u'Articles'), True,)

    class Meta:
        model = Newsletter
        widgets = {
                    # 'sites': chosenwidgets.ChosenSelectMultiple(),
                    'lists': chosenwidgets.ChosenSelectMultiple(),}
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
    # inlines = [NewsletterSendingInline]
    list_display = ('subject','display_lists','sendbutton')
    fieldsets = (
        ('Description', {
            'fields': ['subject', 'template',
                       'content',
                       # 'articles', 'events',
                       'lists'
                       ]
            }),
        )

    # if settings.COOP_USE_SITES:
    #     fieldsets[0][1]['fields'].insert(0, 'sites')
    def display_lists(self,obj):
        listes = []
        for l in obj.lists.all(): listes.append(l.name)
        return mark_safe(', '.join(listes))
    display_lists.short_description = 'Destinataires'
    display_lists.allow_tags = True

    def sendbutton(self,obj):
        if obj.lists.count() > 0:
            return mark_safe('<div><input type="button" class="sendnews btn btn-success" rel="%s" value="Envoyer la lettre"></div>' % obj.pk)
        else:
            return mark_safe(u"Aucun destinataire pour l'instant")
    sendbutton.short_description = 'Envoi'
    sendbutton.allow_tags = True

    def get_urls(self):
        urls = super(NewsletterAdmin, self).get_urls()
        my_urls = patterns('',
            (r'sendnews/(?P<id>\d+)/$', self.admin_site.admin_view(self.sendnews)),
        )
        return my_urls + urls
 
    def sendnews(self, request, id):
        context = {}
        if Newsletter.objects.filter(pk=id).exists():
            news = Newsletter.objects.get(pk=id)
            if news.lists.count() == 0:
                context['msg'] = u'Aucune liste de diffusion destinataire'
            else:
                try:
                    from django.core.management import call_command
                    # from StringIO import StringIO
                    # content = StringIO()
                    call_command('post_newsletter', newsletter=id)#, stdout=content)
                    # content.seek(0)
                    # msg = content.read()
                    context['msg'] = u'lettre envoyée'
                except, e:
                    context['msg'] = u"Erreur d'envoi : %s" % e
        else:
            context['msg'] = u'Erreur : Lettre non trouvée'

        return render_to_response('mailing/admin/sendnews.html', context , context_instance=RequestContext(request))


