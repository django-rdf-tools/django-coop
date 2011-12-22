# -*- coding:utf-8 -*-
from django.contrib import admin
from coop.membre.models import BaseMembre
from coop.initiative.models import BaseRole,BaseEngagement,BaseInitiative,BaseOrganizationCategory
from coop.place.models import BaseSite
from skosxl.models import Label
from coop_geo.models import Location,Located
from django import forms
from django.db import models
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models.loading import get_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.generic import GenericStackedInline

from coop.autocomplete_admin import FkAutocompleteAdmin,InlineAutocompleteAdmin

class BaseEngagementInline(InlineAutocompleteAdmin):
    model = BaseEngagement
    related_search_fields = {'membre': ('nom','prenom','email','user__username'), }
    extra=2

# class BaseSiteInline(admin.StackedInline,InlineAutocompleteAdmin):
#     model = BaseSite
#     related_search_fields = {'location': ('location__label','location__adr1','location__adr2','location__zipcode','location_city'), }
#     extra=0
# 
#         
class LocatedInline(GenericStackedInline,InlineAutocompleteAdmin):
    model = Located
    related_search_fields = {'location': ('label','adr1','adr2','zipcode','city'), }
    extra=1

class BaseInitiativeAdminForm(forms.ModelForm):
    # tags = forms.ModelMultipleChoiceField(
    #     queryset=Label.objects.all().order_by('name'),
    #     widget=FilteredSelectMultiple('tags', False)
    # )
    class Meta:
        model = BaseInitiative


def create_action(category):
    def add_cat(modeladmin, request, queryset):
        for obj in queryset:obj.category.add(category)
    name = "cat_%s" % (category.slug,)
    return (name, (add_cat, name, _(u'Add to the "%s" category') % (category,)))


class BaseInitiativeAdmin(FkAutocompleteAdmin):
    form = BaseInitiativeAdminForm
    list_display = ('title','active','uri')
    list_display_links =('title',)
    search_fields = ['title','acronym','description']
    list_filter = ('active','category')
    ordering = ('title',)
    inlines = [
            LocatedInline,BaseEngagementInline
        ]
    def get_actions(self, request):
        myactions = dict(create_action(s) for s in get_model('coop_local','OrganizationCategory').objects.all())
        return dict(myactions, **super(BaseInitiativeAdmin, self).get_actions(request))#merge des deux dicts
        
        
from coop_geo.widgets import ChooseLocationWidget, LocationPointWidget   
class BaseMembreAdmin(admin.ModelAdmin):
    list_display = ('nom','prenom','email','has_user_account','has_role')
    list_filter = ('category',)
    list_display_links =('nom','prenom')
    search_fields = ('nom','prenom','email')
    ordering = ('nom',)
    widgets = { 'location' : ChooseLocationWidget(None)}
    fieldsets = ()


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
    
    

