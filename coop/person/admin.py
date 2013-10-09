# -*- coding:utf-8 -*-
from django.contrib import admin
from django.conf import settings
from django import forms
from coop.org.admin import create_action, ContactInline, OrgInline
from django.db.models.loading import get_model
from coop_local.models import Contact, Subscription
from chosen import widgets as chosenwidgets
from coop.utils.autocomplete_admin import FkAutocompleteAdmin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _




class PersonAdminForm(forms.ModelForm):
    # category = chosenforms.ChosenModelMultipleChoiceField(
    #         required=False,
    #         overlay=_(u"Choose one or more categories"),
    #         queryset=get_model('coop_local', 'PersonCategory').objects.all())

    class Meta:
        widgets = {'category': chosenwidgets.ChosenSelectMultiple(),
                    'sites': chosenwidgets.ChosenSelectMultiple()}

    def __init__(self, *args, **kwargs):
        super(PersonAdminForm, self).__init__(*args, **kwargs)
        self.fields['category'].help_text = None
        self.fields['location'].help_text = None
        person_contacts = Contact.objects.filter(
            Q(content_type=ContentType.objects.get(model='person'), object_id=self.instance.id)
            )
        self.fields['pref_email'].queryset = person_contacts.filter(contact_medium_id=8)

        if 'sites' in self.fields:
            self.fields['sites'].help_text = None


def person_mobile_phone(obj):
    mob = obj.contacts.filter(contact_medium_id=2)
    if mob.exists():
        return mob[0].content
    else:
        return ""
person_mobile_phone.short_description = 'Mobile'

def person_phone(obj):
    mob = obj.contacts.filter(contact_medium_id=1)
    if mob.exists():
        return mob[0].content
    else:
        return ""
person_phone.short_description = 'Fixe'

def person_email(obj):
    mob = obj.contacts.filter(contact_medium_id=8)
    if mob.exists():
        return mob[0].content
    else:
        return ""
person_email.short_description = 'E-mail'

def person_subs(obj):
    mls = []
    for sub in Subscription.objects.filter(content_type=ContentType.objects.get(model='person'), object_id=obj.id):
        mls.append(sub.mailing_list.name)
    return ", ".join(mls)
person_subs.short_description = 'Mailing'


def ml_action(ml):
    def add_sub(modeladmin, request, queryset):
        # ct = ContentType.objects.get(model='person')
        for obj in queryset:
            ml._instance_to_subscription(obj)
            # if not Subscription.objects.filter(mailing_list=ml, content_type=ct, object_id=obj.id).exists():
            #     Subscription.create(mailing_list=ml, content_object=obj)
    name = "sub_ml_%s" % (ml.id,)
    return (name, (add_sub, name, _(u'Subscribe to mailing list : %s') % (ml.name,)))


class PersonAdmin(FkAutocompleteAdmin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    related_search_fields = {'location': ('label', 'adr1', 'adr2', 'zipcode', 'city'), }

    form = PersonAdminForm
    search_fields = ['last_name', 'first_name', 'pref_email__content']
    list_display = ('last_name', 'first_name', person_mobile_phone, person_phone, person_email, person_subs)
    list_filter = ('category',)
    list_display_links = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name', 'structure')
    ordering = ('last_name',)
    inlines = [ContactInline,
                OrgInline,
                ]

    def get_actions(self, request):
        category_actions = dict(create_action(s) for s in get_model('coop_local', 'PersonCategory').objects.all())
        mailing_actions = dict(ml_action(s) for s in get_model('coop_local', 'MailingList').objects.all())
        my_actions = dict(category_actions, **mailing_actions)
        return dict(my_actions, **super(PersonAdmin, self).get_actions(request))  # merging two dicts

    fieldsets = (
        ('Identification', {
            'fields': ['first_name', 'last_name', 'pref_email',
                        ('location', 'location_display'),  # Using coop-geo
                        'category'
                        ],
            }),
        ('Notes', {
            'fields': ('structure', 'notes',)
        })
    )

    if settings.COOP_USE_SITES:
        fieldsets[0][1]['fields'].insert(0, 'sites')


