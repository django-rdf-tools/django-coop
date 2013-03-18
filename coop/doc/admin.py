# -*- coding:utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django import forms
#from coop_local.models import Attached
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin, NoLookupsFkAutocompleteAdmin
from django.contrib.contenttypes.generic import GenericTabularInline
from django.utils.translation import ugettext_lazy as _
from django.db.models.loading import get_model
from media_tree.forms import FileForm
from media_tree.models import FileNode
from media_tree.widgets import AdminThumbWidget
from sorl.thumbnail.admin import AdminImageMixin
from tinymce.widgets import AdminTinyMCE
from coop.link.admin import LinksInline
from coop.org.admin import URLFieldWidget
from django.db.models import URLField


class MyFileForm(FileForm):
    class Meta:
        fields = ['parent', 'file', 'title']
        widgets = {'file': AdminThumbWidget()}


class AttachmentsInline(GenericTabularInline):
    model = get_model('coop_local', 'Attachment')
    form = MyFileForm
    verbose_name = _(u'Attachment')
    verbose_name_plural = _(u'Attachements')
    extra = 1


class ResourceAdminForm(forms.ModelForm):
    description = forms.CharField(widget=AdminTinyMCE(attrs={'cols': 80, 'rows': 60}), required=False)

    class Meta:
        model = get_model('coop_local', 'DocResource')


class ResourceAdmin(NoLookupsFkAutocompleteAdmin, AdminImageMixin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    form = ResourceAdminForm
    list_display = ('logo_list_display', 'label', 'organization_display')
    list_display_links = ('logo_list_display', 'label')
    list_filter = ('category')
    fieldsets = (
        ('Description', {'fields': ('logo', 'label', 'category', 'description',
                                    'organization', 'remote_organization_label', 'remote_organization_uri',
                                    'person', 'remote_person_label', 'remote_person_uri',
                                    'tags',)
                         }),
        ('Details', {'fields': ('notes', 'page_url', 'file_url', 'zone')
                     }),
    )
    search_fields = ('label', 'description')
    related_search_fields = {'person': ('last_name', 'first_name',
                                        'email', 'structure', 'username'),
                             'organization': ('title', 'acronym', 'subtitle', 'description'),
                             }
    inlines = [AttachmentsInline, LinksInline]
    formfield_overrides = {
        URLField: {'widget': URLFieldWidget},
    }

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(ResourceAdmin, self).get_form(request, obj, **kwargs)
