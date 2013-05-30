# -*- coding:utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, NoLookupsFkAutocompleteAdmin
from sorl.thumbnail.admin import AdminImageMixin
from django import forms
from tinymce.widgets import AdminTinyMCE
from django.db.models.loading import get_model
from chosen import widgets as chosenwidgets
from coop_tag.settings import get_class
from django.contrib.sites.models import Site

#from feincms.admin import tree_editor

# TODO : find a nice generic object widget display


class TaggedItemsInline(admin.StackedInline):
    model = get_class('taggeditem')
    extra = 0

# We just override the TreeEditor template to move columns
# CSS added in coop_tag is here in our admin css sheet

# class CoopTagTreeAdmin(tree_editor.TreeEditor):

#     def changelist_view(self, request, extra_context=None, *args, **kwargs):
#         if 'actions_column' not in self.list_display:
#             self.list_display.insert(0, 'actions_column')
#         return super(CoopTagTreeAdmin, self).changelist_view(request, extra_context)

    # inlines = [
    #     TaggedItemInline
    # ]


class TagAdminForm(forms.ModelForm):
    description = forms.CharField(widget=AdminTinyMCE(attrs={'cols': 80, 'rows': 60}), required=False)

    def __init__(self, *args, **kwargs):
        super(TagAdminForm, self).__init__(*args, **kwargs)
        self.fields['sites'].help_text = None

    class Meta:
        model = get_model('coop_local', 'Tag')
        widgets = {'sites': chosenwidgets.ChosenSelectMultiple(),
                   }

    def clean(self):
        """Make sure tag is available for all sites."""
        sites = list(self.cleaned_data['sites'])
        for s in Site.objects.all():
            if not s in sites:
                # print u'%s not listed' % s
                sites.append(s)
        self.cleaned_data['sites'] = sites
        return self.cleaned_data


class TagAdmin(NoLookupsFkAutocompleteAdmin, AdminImageMixin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    form = TagAdminForm
    list_display = ('name',) # 'active')
    # list_editable = ('active',)
    list_display_links = ('name', )
    ordering = ('name',)
    fieldsets = (
        (_('Description'), {'fields': ('sites', 'logo', 'name', 'description', 
                                    'person', 'remote_person_label', 'remote_person_uri',
                                    'active',
                                    )
                         }),
    )
    search_fields = ('name', 'slug', 'description')
    related_search_fields = {'person': ('last_name', 'first_name',
                                        'email', 'structure', 'username'),
                             }
    inlines = [TaggedItemsInline]
