# -*- coding:utf-8 -*-
from django.contrib import admin
from coop.org.models import BaseEngagement, BaseRelation
from coop.person.models import BasePerson
from coop.exchange.models import BaseExchange, BasePaymentModality, BaseTransaction, BaseProduct
from django.db import models
from django import forms
from django.conf import settings

# from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models.loading import get_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.generic import GenericTabularInline
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


class SimpleLinkWidget(forms.Widget):
    def __init__(self, obj, attrs=None):
        self.object = obj
        super(SimpleLinkWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if self.object.pk:
            return mark_safe(
                u'<a target="_blank" href="../../../%s/%s/%s/">%s</a>' %\
                      (
                       self.object._meta.app_label,
                       self.object._meta.object_name.lower(),
                       self.object.pk, 
                       u'<b>Compléter la fiche détaillée</b>'
                       )
            )
        else:
            return mark_safe(u'')


class M2MLinkWidget(forms.Widget):
    def __init__(self, obj, fkey_name, attrs=None,):
        self.object = obj
        self.fkey = fkey_name
        super(M2MLinkWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if self.object.pk and self.fkey and getattr(self.object, self.fkey) != None:
            return mark_safe(u'<a href="../../../%s/%s/%s/">%s</a>' % \
                (self.object._meta.app_label,
                    getattr(self.object, self.fkey)._meta.object_name.lower(), 
                    getattr(self.object, self.fkey).pk, 
                    u' '.join((u'Fiche', unicode(self.fkey)))  # TODO how to get the translated app name ?
                    )
            )
        else:
            return mark_safe(u'')


class ExchangeInlineLinkForm(forms.ModelForm):
    class Meta:
        model = BaseExchange
    lien = forms.CharField(label='lien', required=False)

    def __init__(self, *args, **kwargs):
        super(ExchangeInlineLinkForm, self).__init__(*args, **kwargs)
        self.fields['lien'].widget = SimpleLinkWidget(self.instance)        


class ContactInlineLinkForm(forms.ModelForm):
    lien = forms.CharField(label='lien', required=False)

    def __init__(self, *args, **kwargs):
        super(ContactInlineLinkForm, self).__init__(*args, **kwargs)
        self.fields['lien'].widget = M2MLinkWidget(self.instance, fkey_name='person')


class OrgInlineLinkForm(forms.ModelForm):
    lien = forms.CharField(label='lien', required=False)

    def __init__(self, *args, **kwargs):
        super(OrgInlineLinkForm, self).__init__(*args, **kwargs)
        self.fields['lien'].widget = M2MLinkWidget(self.instance, fkey_name='organization')


# ---------- if coop-geo is installed --------------

if "coop_geo" in settings.INSTALLED_APPS:
    from coop_geo.forms import AreaFormForInline
    from coop_geo.models import AreaLink, Located

    class LocatedInlineLinkForm(forms.ModelForm):
        lien = forms.CharField(label='lien', required=False)

        def __init__(self, *args, **kwargs):
            super(LocatedInlineLinkForm, self).__init__(*args, **kwargs)
            self.fields['lien'].widget = M2MLinkWidget(self.instance, fkey_name='location')

    class LocatedInline(GenericTabularInline, InlineAutocompleteAdmin):
        form = LocatedInlineLinkForm
        model = Located
        related_search_fields = {'location': ('label', 'adr1', 'adr2', 'zipcode', 'city'), }
        extra = 1

    class AreaInline(GenericTabularInline):
        form = AreaFormForInline
        related_search_fields = {'location': ('label', 'reference'), }
        model = AreaLink
        extra = 1

        def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
            associated_obj = None
            if db_field.name == "location":
                if request._obj_ is not None:
                    associated_obj = request._obj_
            r = super(AreaInline, self).formfield_for_foreignkey(db_field,
                                                          request, **kwargs)
            # decorate the modelform in order to use it in the area widget
            r._associated_obj = request._obj_
            return r

# ----------------------------------------------------


class URLFieldWidget(AdminURLFieldWidget):
    def render(self, name, value, attrs=None):
        widget = super(URLFieldWidget, self).render(name, value, attrs)
        return mark_safe(u'%s&nbsp;&nbsp;<a href="#" onclick="window.'
                         u'open(document.getElementById(\'%s\')'
                         u'.value);return false;" />Afficher</a>' % (widget, attrs['id']))


class BaseEngagementInline(InlineAutocompleteAdmin):
    form = ContactInlineLinkForm
    model = BaseEngagement
    related_search_fields = {'person': ('last_name', 'first_name', 'email', 'structure', 'username'), }
    extra = 2


class BaseOrgInline(InlineAutocompleteAdmin):
    form = OrgInlineLinkForm
    model = BaseEngagement
    related_search_fields = {'organization': ('title', 'subtitle', 'description'), }
    extra = 1


class BasePaymentInline(admin.TabularInline):
    model = BasePaymentModality
    extra = 0


class BaseExchangeInline(admin.StackedInline):
    #form = ExchangeInlineLinkForm #needed to include a link to the change_form / only because nested inlines are not possible
    model = BaseExchange
    fieldsets = ((None, {'fields': ('title',
                                    ('etype', 'permanent', 'expiration'),
                                    'description',
                                    #'lien'
                                    )}),)
    extra = 1
    #class Media: js = ('js/expiration.js',)


class BaseProductInline(admin.StackedInline):
    model = BaseProduct
    fieldsets = ((None, {'fields': ('title',
                                    'description',
                                    )}),)
    extra = 1


class BaseTransactionInline(admin.StackedInline):
    model = BaseTransaction
    fk_name = 'destination_org'
    fieldsets = ((None, {'fields': ('title', 'origin', 'description')}),)
    related_search_fields = {'origin': ('title', 'description', 'organization__title'), }
    extra = 1


class BaseRelationInline(InlineAutocompleteAdmin):
    model = BaseRelation
    fk_name = 'source'
    readonly_fields = ('created',)
    fields = ('reltype', 'target', 'confirmed', 'created')
    related_search_fields = {'target': ('title', 'subtitle', 'description'), }
    extra = 1
       

from chosen import forms as chosenforms
from chosen import widgets as chosenwidgets
   

class BaseOrganizationAdminForm(forms.ModelForm):
    class Meta:
        widgets = {'category': chosenwidgets.ChosenSelectMultiple()}

    def __init__(self, *args, **kwargs):
        super(BaseOrganizationAdminForm, self).__init__(*args, **kwargs)
        engagements = self.instance.engagement_set.all()
        members_id = engagements.values_list('person_id', flat=True)
        print members_id
        org_contacts = Contact.objects.filter(
            Q(content_type=ContentType.objects.get(model='organization'), object_id=self.instance.id)
          | Q(content_type=ContentType.objects.get(model='person'), object_id__in=members_id)
            )
        self.fields['pref_email'].queryset = org_contacts.filter(category=8)
        self.fields['pref_phone'].queryset = org_contacts.filter(category=1)
        
        member_locations_id = [m.location.id for m in 
            Person.objects.filter(id__in=members_id).exclude(location=None)]  # limit SQL to location field

        self.fields['pref_address'].queryset = Location.objects.filter(
            Q(id__in=self.instance.located.all().values_list('location_id', flat=True))
          | Q(id__in=member_locations_id)
            )


class BaseExchangeAdmin(ForeignKeyAutocompleteAdmin):  # AdminImageMixin, 
    fieldsets = ((None, {
            'fields': (('etype', 'permanent', 'expiration', ), 'title', 'description',
                       'organization'
                       )
            }),)
    related_search_fields = {'organization': ('title', 'subtitle', 'description'), }


def create_action(category):
    def add_cat(modeladmin, request, queryset):
        for obj in queryset:
            obj.category.add(category)
    name = "cat_%s" % (category.slug,)
    return (name, (add_cat, name, _(u'Add to the "%s" category') % (category,)))


class BaseOrganizationAdmin(AdminImageMixin, FkAutocompleteAdmin):
    form = BaseOrganizationAdminForm
    list_display = ('logo_thumb', 'title', 'active', 'has_description',)
    list_display_links = ('title', )
    search_fields = ['title', 'subtitle', 'description']
    list_filter = ('active', 'category')
    actions_on_top = True
    actions_on_bottom = True
    save_on_top = True
    #filter_horizontal = ('category',)
    list_per_page = 10
    list_select_related = True
    #read_only_fields = ['created','modified']
    ordering = ('title',)
    formfield_overrides = {
        URLField: {'widget': URLFieldWidget},
    }
    inlines = [  # overriden in coop_local
                        BaseEngagementInline,
                        # LocatedInline,
                        # AreaInline,
                        BaseRelationInline,
                        BaseExchangeInline,
                        ]
    fieldsets = (
        (None, {
            'fields': ('logo', 'title', 'subtitle', ('birth', 'active',),
                        'web',
                        'pref_email',
                        'pref_phone',
                        'pref_address',
                        'description', 'category',
                        )
            }),
        ('Notes', {
            'classes': ('collapse',),
            'fields': ('notes',)
        })
    )

    def get_actions(self, request):
        myactions = dict(create_action(s) for s in get_model('coop_local', 'OrganizationCategory').objects.all())
        return dict(myactions, **super(BaseOrganizationAdmin, self).get_actions(request))  # merging two dicts
        #list_display = ['my_image_thumb', 'my_other_field1', 'my_other_field2', ] ???

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(BaseOrganizationAdmin, self).get_form(request, obj, **kwargs)

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
 

class BasePersonAdminForm(forms.ModelForm):
    # model = BasePerson
    # category = chosenforms.ChosenModelMultipleChoiceField(
    #         required=False,
    #         overlay=_(u"Choose one or more categories"),
    #         queryset=get_model('coop_local', 'PersonCategory').objects.all())    
    class Meta:
        widgets = {'category': chosenwidgets.ChosenSelectMultiple()}


class BasePersonAdmin(ForeignKeyAutocompleteAdmin):  # FkAutocompleteAdmin too but...
    form = BasePersonAdminForm
    list_display = ('last_name', 'first_name', 'email', 'structure', 'has_user_account', 'has_role')
    list_filter = ('category',)
    list_display_links = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name', 'email', 'structure')    
    ordering = ('last_name',)
    # inlines = [ContactInline,
    #             OrgInline,
    #             SeeAlsoInline,
    #             ]

    def get_actions(self, request):
        myactions = dict(create_action(s) for s in get_model('coop_local', 'PersonCategory').objects.all())
        return dict(myactions, **super(BasePersonAdmin, self).get_actions(request))  # merging two dicts
    
    fieldsets = (
        (None, {
            'fields': (('first_name', 'last_name'),
                        'email',
                        'category'
                        ),
            }),
        ('Notes', {
            'classes': ('collapse',),
            'fields': ('structure', 'notes',)
        })
    )


from django.contrib.admin.filterspecs import FilterSpec, RelatedFilterSpec
from django.contrib.admin.util import get_model_from_relation
from django.db.models import Count


if "coop_tag" in settings.INSTALLED_APPS:

    #from taggit.managers import TaggableManager
    from taggit_autosuggest.managers import TaggableManager

    class TaggitFilterSpec(RelatedFilterSpec):
        """
        A FilterSpec that can be used to filter by taggit tags in the admin.
        To use, simply import this module (for example in `models.py`), and add the
        name of your :class:`taggit.managers.TaggableManager` field in the
        :attr:`list_filter` attribute of your :class:`django.contrib.ModelAdmin`
        class.
        """

        def __init__(self, f, request, params, model, model_admin,
                     field_path=None):
            super(RelatedFilterSpec, self).__init__(
                f, request, params, model, model_admin, field_path=field_path)

            other_model = get_model_from_relation(f)
            if isinstance(f, (models.ManyToManyField,
                              models.related.RelatedObject)):
                # no direct field on this model, get name from other model
                self.lookup_title = other_model._meta.verbose_name
            else:
                self.lookup_title = f.verbose_name  # use field name
            rel_name = other_model._meta.pk.name
            self.lookup_kwarg = '%s__%s__exact' % (self.field_path, rel_name)
            self.lookup_kwarg_isnull = '%s__isnull' % (self.field_path)
            self.lookup_val = request.GET.get(self.lookup_kwarg, None)
            self.lookup_val_isnull = request.GET.get(
                                          self.lookup_kwarg_isnull, None)
            # Get tags and their count
            # through_opts = f.through._meta
            # count_field = ("%s_%s_items" % (through_opts.app_label,
            #         through_opts.object_name)).lower()
            
            queryset = getattr(f.model, f.name).all()
            queryset = queryset.annotate(num_times=Count('ctagged_items'))
            queryset = queryset.order_by("-num_times")
            self.lookup_choices = [(t.pk, "%s (%s)" % (t.name, t.num_times)) 
                    for t in queryset[:20]]


    # HACK: we insert the filter at the beginning of the list to avoid the manager
    # to be picked as a RelatedFilterSpec
    FilterSpec.filter_specs.insert(0, (lambda f: isinstance(f, TaggableManager),
        TaggitFilterSpec))
