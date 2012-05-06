# # -*- coding:utf-8 -*-
# from django.contrib import admin
# from coop.org.models import BaseEngagement, BaseRelation
# from coop.person.models import BasePerson
# from coop.exchange.models import BaseExchange, BasePaymentModality, BaseTransaction, BaseProduct
# from django import forms
# from django.conf import settings

# # from django.contrib.admin.widgets import FilteredSelectMultiple
# from django.db.models.loading import get_model
# from django.utils.translation import ugettext_lazy as _
# from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin
# from django_extensions.admin import ForeignKeyAutocompleteAdmin

# from coop_local.models import Contact, Person
# from coop_geo.models import Location
# from django.contrib.contenttypes.models import ContentType
# from django.db.models import Q

# from django.contrib.admin.widgets import AdminURLFieldWidget
# from django.db.models import URLField
# from django.utils.safestring import mark_safe

# from sorl.thumbnail.admin import AdminImageMixin

# from sorl.thumbnail import default
# ADMIN_THUMBS_SIZE = '60x60'


# class SimpleLinkWidget(forms.Widget):
#     def __init__(self, obj, attrs=None):
#         self.object = obj
#         super(SimpleLinkWidget, self).__init__(attrs)

#     def render(self, name, value, attrs=None):
#         if self.object.pk:
#             return mark_safe(
#                 u'<a target="_blank" href="../../../%s/%s/%s/">%s</a>' %\
#                       (
#                        self.object._meta.app_label,
#                        self.object._meta.object_name.lower(),
#                        self.object.pk, 
#                        u'<b>Compléter la fiche détaillée</b>'
#                        )
#             )
#         else:
#             return mark_safe(u'')


# class M2MLinkWidget(forms.Widget):
#     def __init__(self, obj, fkey_name, attrs=None,):
#         self.object = obj
#         self.fkey = fkey_name
#         super(M2MLinkWidget, self).__init__(attrs)

#     def render(self, name, value, attrs=None):
#         if self.object.pk and self.fkey and getattr(self.object, self.fkey) != None:
#             return mark_safe(u'<a href="../../../%s/%s/%s/">%s</a>' % \
#                 (self.object._meta.app_label,
#                     getattr(self.object, self.fkey)._meta.object_name.lower(), 
#                     getattr(self.object, self.fkey).pk, 
#                     u' '.join((u'Fiche', unicode(self.fkey)))  # TODO how to get the translated app name ?
#                     )
#             )
#         else:
#             return mark_safe(u'')


# class ExchangeInlineLinkForm(forms.ModelForm):
#     class Meta:
#         model = BaseExchange
#     lien = forms.CharField(label='lien', required=False)

#     def __init__(self, *args, **kwargs):
#         super(ExchangeInlineLinkForm, self).__init__(*args, **kwargs)
#         self.fields['lien'].widget = SimpleLinkWidget(self.instance)        


# class ContactInlineLinkForm(forms.ModelForm):
#     lien = forms.CharField(label='lien', required=False)

#     def __init__(self, *args, **kwargs):
#         super(ContactInlineLinkForm, self).__init__(*args, **kwargs)
#         self.fields['lien'].widget = M2MLinkWidget(self.instance, fkey_name='person')


# class OrgInlineLinkForm(forms.ModelForm):
#     lien = forms.CharField(label='lien', required=False)

#     def __init__(self, *args, **kwargs):
#         super(OrgInlineLinkForm, self).__init__(*args, **kwargs)
#         self.fields['lien'].widget = M2MLinkWidget(self.instance, fkey_name='organization')


# # ---------- if coop-geo is installed --------------

# if "coop_geo" in settings.INSTALLED_APPS:
#     from coop_geo.admin import LocatedInline, AreaInline

# # ----------------------------------------------------






 

# # from django.contrib.admin.filterspecs import FilterSpec, RelatedFilterSpec
# # from django.contrib.admin.util import get_model_from_relation
# # from django.db.models import Count


# # if "coop_tag" in settings.INSTALLED_APPS:

# #     #from taggit.managers import TaggableManager
# #     from taggit_autosuggest.managers import TaggableManager

# #     class TaggitFilterSpec(RelatedFilterSpec):
# #         """
# #         A FilterSpec that can be used to filter by taggit tags in the admin.
# #         To use, simply import this module (for example in `models.py`), and add the
# #         name of your :class:`taggit.managers.TaggableManager` field in the
# #         :attr:`list_filter` attribute of your :class:`django.contrib.ModelAdmin`
# #         class.
# #         """

# #         def __init__(self, f, request, params, model, model_admin,
# #                      field_path=None):
# #             super(RelatedFilterSpec, self).__init__(
# #                 f, request, params, model, model_admin, field_path=field_path)

# #             other_model = get_model_from_relation(f)
# #             if isinstance(f, (models.ManyToManyField,
# #                               models.related.RelatedObject)):
# #                 # no direct field on this model, get name from other model
# #                 self.lookup_title = other_model._meta.verbose_name
# #             else:
# #                 self.lookup_title = f.verbose_name  # use field name
# #             rel_name = other_model._meta.pk.name
# #             self.lookup_kwarg = '%s__%s__exact' % (self.field_path, rel_name)
# #             self.lookup_kwarg_isnull = '%s__isnull' % (self.field_path)
# #             self.lookup_val = request.GET.get(self.lookup_kwarg, None)
# #             self.lookup_val_isnull = request.GET.get(
# #                                           self.lookup_kwarg_isnull, None)
# #             # Get tags and their count
# #             # through_opts = f.through._meta
# #             # count_field = ("%s_%s_items" % (through_opts.app_label,
# #             #         through_opts.object_name)).lower()
            
# #             queryset = getattr(f.model, f.name).all()
# #             queryset = queryset.annotate(num_times=Count('ctagged_items'))
# #             queryset = queryset.order_by("-num_times")
# #             self.lookup_choices = [(t.pk, "%s (%s)" % (t.name, t.num_times)) 
# #                     for t in queryset[:20]]


# #     # HACK: we insert the filter at the beginning of the list to avoid the manager
# #     # to be picked as a RelatedFilterSpec
# #     FilterSpec.filter_specs.insert(0, (lambda f: isinstance(f, TaggableManager),
# #         TaggitFilterSpec))
