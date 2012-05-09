# -*- coding:utf-8 -*-
from django.contrib import admin
from coop.org.models import BaseEngagement, BaseRelation
from coop.person.models import BasePerson
#from coop.exchange.models import BaseExchange, BasePaymentModality, BaseTransaction, BaseProduct
from coop.exchange.admin import ExchangeInline
from django import forms
from django.conf import settings

# from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models.loading import get_model
from django.utils.translation import ugettext_lazy as _
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin
from django_extensions.admin import ForeignKeyAutocompleteAdmin

from coop_local.models import Contact, Person
from coop_geo.models import Location
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from django.contrib.admin.widgets import AdminURLFieldWidget
from django.db.models import URLField
from django.utils.safestring import mark_safe

from sorl.thumbnail.admin import AdminImageMixin

from sorl.thumbnail import default
ADMIN_THUMBS_SIZE = '60x60'      

from chosen import widgets as chosenwidgets


if "coop_geo" in settings.INSTALLED_APPS:
    from coop_geo.admin import LocatedInline, AreaInline

from django.contrib.contenttypes.generic import GenericTabularInline
from tinymce.widgets import AdminTinyMCE


class URLFieldWidget(AdminURLFieldWidget):
    def render(self, name, value, attrs=None):
        widget = super(URLFieldWidget, self).render(name, value, attrs)
        return mark_safe(u'%s&nbsp;&nbsp;<a href="#" onclick="window.'
                         u'open(document.getElementById(\'%s\')'
                         u'.value);return false;" class="btn btn-mini"/>Afficher dans une nouvelle fenêtre</a>' % (widget, attrs['id']))


class ContactInline(GenericTabularInline):
    model = get_model('coop_local', 'Contact')
    verbose_name = _(u'Contact information')
    verbose_name_plural = _(u'Contact informations')
    extra = 1


class EngagementInline(InlineAutocompleteAdmin):
    model = get_model('coop_local', 'Engagement')
    verbose_name = _(u'Member')
    verbose_name_plural = _(u'Members')
    related_search_fields = {'person': ('last_name', 'first_name',
                                        'email', 'structure', 'username'), }
    extra = 2


class RelationInline(InlineAutocompleteAdmin):
    model = get_model('coop_local', 'Relation')
    fk_name = 'source'
    readonly_fields = ('created',)
    fields = ('reltype', 'target', 'confirmed', 'created')
    related_search_fields = {'target': ('title', 'subtitle', 'description'), }
    extra = 1


class OrgInline(InlineAutocompleteAdmin):
    model = get_model('coop_local', 'Engagement')
    verbose_name = _(u'Engagement')
    verbose_name_plural = _(u'Engagements')
    related_search_fields = {'organization': ('title', 'subtitle', 'description'), }
    extra = 1


class OrganizationAdminForm(forms.ModelForm):
    description = forms.CharField(widget=AdminTinyMCE(attrs={'cols': 80, 'rows': 60}))

    class Meta:
        model = get_model('coop_local', 'Organization')
        widgets = {'category': chosenwidgets.ChosenSelectMultiple()}

    def __init__(self, *args, **kwargs):
        super(OrganizationAdminForm, self).__init__(*args, **kwargs)
        engagements = self.instance.engagement_set.all()
        members_id = engagements.values_list('person_id', flat=True)
        print members_id
        org_contacts = Contact.objects.filter(
            Q(content_type=ContentType.objects.get(model='organization'), object_id=self.instance.id)
          | Q(content_type=ContentType.objects.get(model='person'), object_id__in=members_id)
            )
        self.fields['pref_email'].queryset = org_contacts.filter(category=8)
        self.fields['pref_phone'].queryset = org_contacts.filter(category=1)
        self.fields['category'].help_text = None

        member_locations_id = [m.location.id for m in 
            Person.objects.filter(id__in=members_id).exclude(location=None)]  # limit SQL to location field

        self.fields['pref_address'].queryset = Location.objects.filter(
            Q(id__in=self.instance.located.all().values_list('location_id', flat=True))
          | Q(id__in=member_locations_id)
            )


def create_action(category):
    def add_cat(modeladmin, request, queryset):
        for obj in queryset:
            obj.category.add(category)
    name = "cat_%s" % (category.slug,)
    return (name, (add_cat, name, _(u'Add to the "%s" category') % (category,)))


class OrganizationAdmin(AdminImageMixin, FkAutocompleteAdmin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html' 
    form = OrganizationAdminForm
    list_display = ['logo_thumb', 'title', 'active', 'has_description', 'has_location']
    list_display_links = ['title', ]
    search_fields = ['title', 'subtitle', 'description']
    list_filter = ['active', 'category']
    #actions_on_top = True
    #actions_on_bottom = True
    #save_on_top = True
    #filter_horizontal = ('category',)
    list_per_page = 10
    list_select_related = True
    #read_only_fields = ['created','modified']
    ordering = ('title',)
    formfield_overrides = {
        URLField: {'widget': URLFieldWidget},
    }
    inlines = [  # this list can be overriden in coop_local
                ContactInline,
                EngagementInline,
                ExchangeInline,
                RelationInline,
                LocatedInline,
                AreaInline,
                ]
    fieldsets = (
        ('Identité', {
            'fields': ('logo', 'title', 'subtitle', ('birth', 'active',),
                        'statut', 'web')
            }),
        ('Description', {
            'fields': ('description', 'category', 'tags', )
            }),

        ('Préférences', {
            #'classes': ('collapse',),
            'fields': ('pref_email', 'pref_phone', 'pref_address', 'notes',)
        })
    )

    def get_actions(self, request):
        myactions = dict(create_action(s) for s in get_model('coop_local', 'OrganizationCategory').objects.all())
        return dict(myactions, **super(OrganizationAdmin, self).get_actions(request))  # merging two dicts
        #list_display = ['my_image_thumb', 'my_other_field1', 'my_other_field2', ] ???

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(OrganizationAdmin, self).get_form(request, obj, **kwargs)

    def logo_thumb(self, obj):
        if obj.logo:
            thumb = default.backend.get_thumbnail(obj.logo.file, ADMIN_THUMBS_SIZE)
            return '<img width="%s" src="%s" />' % (thumb.width, thumb.url)
        else:
            return _(u"No Image") 
    logo_thumb.short_description = _(u"logo")
    logo_thumb.allow_tags = True

    class Media:
        js = ('/static/js/admin_customize.js',)
 
