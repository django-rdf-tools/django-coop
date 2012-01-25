# -*- coding:utf-8 -*-
from django.contrib import admin
from coop.initiative.models import BaseEngagement,BaseInitiative,\
    BaseOrganizationCategory,BaseRelation
from coop.membre.models import BaseMembre
from coop_geo.models import AreaLink,Located
from django.db import models
from django import forms

from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models.loading import get_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.generic import GenericStackedInline,GenericTabularInline
from coop.utils.autocomplete_admin import FkAutocompleteAdmin,InlineAutocompleteAdmin

from django.contrib.admin.widgets import AdminURLFieldWidget
from django.db.models import URLField
from django.utils.safestring import mark_safe

from sorl.thumbnail.admin import AdminImageMixin

from sorl.thumbnail import default
ADMIN_THUMBS_SIZE = '60x60'

class LinkWidget(forms.Widget):
    def __init__(self, obj, fkey_name, attrs=None,):
        self.object = obj
        self.fkey = fkey_name
        super(LinkWidget, self).__init__(attrs)
    def render(self, name, value, attrs=None):
        if self.object.pk:
            return mark_safe(u'<a href="../../../%s/%s/%s/" target="_blank">%s</a>' % (self.object._meta.app_label,
                    getattr(self.object,self.fkey)._meta.object_name.lower(), getattr(self.object,self.fkey).pk, u'Fiche d√©taill√©e'))
        else:
            return mark_safe(u'')


class ContactInlineLinkForm(forms.ModelForm):
    link = forms.CharField(label='link', required=False)
    def __init__(self, *args, **kwargs):
        super(ContactInlineLinkForm, self).__init__(*args, **kwargs)
        self.fields['link'].widget = LinkWidget(self.instance,fkey_name='membre')


class IntiativeInlineLinkForm(forms.ModelForm):
    link = forms.CharField(label='link', required=False)
    def __init__(self, *args, **kwargs):
        super(ContactInlineLinkForm, self).__init__(*args, **kwargs)
        self.fields['link'].widget = LinkWidget(self.instance,fkey_name='initiative')


class LocatedInlineLinkForm(forms.ModelForm):
    link = forms.CharField(label='link', required=False)
    def __init__(self, *args, **kwargs):
        super(LocatedInlineLinkForm, self).__init__(*args, **kwargs)
        self.fields['link'].widget = LinkWidget(self.instance,fkey_name='location')


class URLFieldWidget(AdminURLFieldWidget):
    def render(self, name, value, attrs=None):
        widget = super(URLFieldWidget, self).render(name, value, attrs)
        return mark_safe(u'%s&nbsp;&nbsp;<a href="#" onclick="window.'
                         u'open(document.getElementById(\'%s\')'
                         u'.value);return false;" />Ì†ºÌºè</a>' % (widget, attrs['id']))

class BaseEngagementInline(InlineAutocompleteAdmin):
    form = ContactInlineLinkForm
    model = BaseEngagement
    related_search_fields = {'membre': ('nom','prenom','email','structure','user__username'), }
    extra=2

class BaseEngInitInline(InlineAutocompleteAdmin):
    form = IntiativeInlineLinkForm
    model = BaseEngagement
    related_search_fields = {'initiative': ('title','acronym','description'), }
    extra=1

class BaseRelationInline(InlineAutocompleteAdmin):
    model = BaseRelation
    fk_name = 'source'
    readonly_fields = ('created',)
    fields = ('reltype','target','confirmed','created')
    related_search_fields = {'target': ('title','acronym','description'), }
    extra=1

# class BaseSiteInline(admin.StackedInline,InlineAutocompleteAdmin):
#     model = BaseSite
#     related_search_fields = {'location': ('location__label','location__adr1','location__adr2','location__zipcode','location_city'), }
#     extra=0
# 
#         
class LocatedInline(GenericTabularInline,InlineAutocompleteAdmin):
    form = LocatedInlineLinkForm
    model = Located
    related_search_fields = {'location': ('label','adr1','adr2','zipcode','city'), }
    extra=1

class AreaInline(GenericTabularInline):
    model = AreaLink
    extra=1
 
from chosen import forms as chosenforms
   
class BaseInitiativeAdminForm(forms.ModelForm):
    category = chosenforms.ChosenModelMultipleChoiceField(
            overlay=_(u"Choose one or more categories"),
            queryset=get_model('coop_local','OrganizationCategory').objects.all())    
    class Meta:
        model = BaseInitiative


class BaseMemberAdminForm(forms.ModelForm):
    category = chosenforms.ChosenModelMultipleChoiceField(
            overlay=_(u"Choose one or more categories"),
            queryset=get_model('coop_local','MemberCategory').objects.all())    
    class Meta:
        model = BaseMembre


def create_action(category):
    def add_cat(modeladmin, request, queryset):
        for obj in queryset:obj.category.add(category)
    name = "cat_%s" % (category.slug,)
    return (name, (add_cat, name, _(u'Add to the "%s" category') % (category,)))


class BaseInitiativeAdmin(AdminImageMixin, FkAutocompleteAdmin):
    # model is not given because the coop_local "true" model will override this
    form = BaseInitiativeAdminForm
    list_display = ('logo_thumb','title','active','has_location','has_description')
    list_display_links =('title',)
    search_fields = ['title','acronym','description']
    list_filter = ('active','category')
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
    inlines = [
            BaseEngagementInline,
            LocatedInline,
            #AreaInline,
            BaseRelationInline
        ]
    fieldsets = (
        (None, {
            'fields' : ('logo','title','acronym',('birth','active',),
                        ('email','web'),('rss','vcal'),'description','category','tags',
                        ('telephone_fixe','mobile')
                        )
                        
            }),
        ('Notes', {
            'classes': ('collapse',),
            'fields': ('notes',)
        })
    )    
    def get_actions(self, request):
        myactions = dict(create_action(s) for s in get_model('coop_local','OrganizationCategory').objects.all())
        return dict(myactions, **super(BaseInitiativeAdmin, self).get_actions(request))#merging two dicts
        #list_display = ['my_image_thumb', 'my_other_field1', 'my_other_field2', ] ???

    def logo_thumb(self, obj):
        if obj.logo:
            thumb = default.backend.get_thumbnail(obj.logo.file, ADMIN_THUMBS_SIZE)
            return '<img width="%s" src="%s" />' % (thumb.width, thumb.url)
        else:
            return _(u"No Image") 
    logo_thumb.short_description = _(u"logo")
    logo_thumb.allow_tags = True
    
      
        
class BaseMembreAdmin(admin.ModelAdmin):
    # model is not given because the coop_local "true" model will override this
    form = BaseMemberAdminForm
    list_display = ('nom','prenom','email','structure','has_user_account','has_role')
    list_filter = ('category',)
    list_display_links =('nom','prenom')
    search_fields = ('nom','prenom','email','structure')
    ordering = ('nom',)
    #inlines = [BaseEngInitInline,]
    def get_actions(self, request):
        myactions = dict(create_action(s) for s in get_model('coop_local','MemberCategory').objects.all())
        return dict(myactions, **super(BaseMembreAdmin, self).get_actions(request))#merging two dicts
    
    fieldsets = (
        (None, {
            'fields' : ('prenom',('nom','pub_name'),
                        ('telephone_fixe','pub_phone'),
                        ('telephone_portable','pub_mobile'),
                        'email','category'),
            }),
        ('Notes', {
            'classes': ('collapse',),
            'fields': ('structure','notes',)
        })
    )


from django.contrib.admin.filterspecs import FilterSpec, RelatedFilterSpec
from django.contrib.admin.util import get_model_from_relation
from django.db.models import Count
from taggit.managers import TaggableManager

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
            self.lookup_title = f.verbose_name # use field name
        rel_name = other_model._meta.pk.name
        self.lookup_kwarg = '%s__%s__exact' % (self.field_path, rel_name)
        self.lookup_kwarg_isnull = '%s__isnull' % (self.field_path)
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_val_isnull = request.GET.get(
                                      self.lookup_kwarg_isnull, None)
        # Get tags and their count
        through_opts = f.through._meta
        count_field = ("%s_%s_items" % (through_opts.app_label,
                through_opts.object_name)).lower()
        queryset = getattr(f.model, f.name).all()
        queryset = queryset.annotate(num_times=Count(count_field))
        queryset = queryset.order_by("-num_times")
        self.lookup_choices = [(t.pk, "%s (%s)" % (t.name, t.num_times)) 
                for t in queryset]


# HACK: we insert the filter at the beginning of the list to avoid the manager
# to be picked as a RelatedFilterSpec
FilterSpec.filter_specs.insert(0, (lambda f: isinstance(f, TaggableManager),
    TaggitFilterSpec))
    
    


