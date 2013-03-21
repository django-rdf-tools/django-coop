# -*- coding:utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django.db import models
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
#from coop.org.admin import URLFieldWidget
from django.db.models import URLField
from django.contrib.admin.widgets import AdminURLFieldWidget
from django.utils.safestring import mark_safe
import pyisbn
from coop.doc.models import ISBNField
from chosen import widgets as chosenwidgets


class ISBNWidget(forms.TextInput):
    def __init__(self, language=None, attrs={}):
        super(ISBNWidget, self).__init__(attrs=attrs)

    def render(self, name, value, attrs={}):
        if (not value) or len(str(value)) < 2:
            return super(ISBNWidget, self).render(name, value, attrs)
        return super(ISBNWidget, self).render(name, value, attrs) + mark_safe("""
            <br />
            <div class="alt">%s-digit: <span class="altisbn">%s <span class="doodad">
                <a href="http://www.librarything.com/isbn/%s">more &#9901;</a>
            </span></span></div>
        """ % (
            (len(str(value)) == 10) and "13" or "10",
            pyisbn.convert(value),
            value
        ))


# obligé de re-déclarer cette classe de coop.org.admin a cause d'une boucle d'import
class URLFieldWidget(AdminURLFieldWidget):
    def render(self, name, value, attrs=None):
        widget = super(URLFieldWidget, self).render(name, value, attrs)
        return mark_safe(u'%s&nbsp;&nbsp;<a href="#" onclick="window.'
                         u'open(document.getElementById(\'%s\')'
                         u'.value);return false;" class="btn btn-mini"/>Afficher dans une nouvelle fenêtre</a>' % (widget, attrs['id']))


class MyFileForm(FileForm):
    class Meta:
        fields = ['parent', 'file', 'title']
        widgets = {'file': AdminThumbWidget()}


class AttachmentsInline(GenericTabularInline):
    model = get_model('coop_local', 'Attachment')
    form = MyFileForm
    verbose_name = _(u'Attachment')
    verbose_name_plural = _(u'Attachments')
    extra = 1


class ResourceAdminForm(forms.ModelForm):
    description = forms.CharField(widget=AdminTinyMCE(attrs={'cols': 80, 'rows': 60}), required=False)

    def __init__(self, *args, **kwargs):
        super(ResourceAdminForm, self).__init__(*args, **kwargs)
        self.fields['category'].help_text = None

    class Meta:
        model = get_model('coop_local', 'DocResource')
        widgets = {'category': chosenwidgets.ChosenSelectMultiple(),}
        

class ResourceAdmin(NoLookupsFkAutocompleteAdmin, AdminImageMixin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    form = ResourceAdminForm
    list_display = ('logo_list_display', 'label', 'organization_display')
    list_display_links = ('logo_list_display', 'label')
    list_filter = ('category',)
    fieldsets = (
        ('Description', {'fields': ('logo', 'label', 'category', 'description',
                                    'organization', 'remote_organization_label', 'remote_organization_uri',
                                    'person', 'remote_person_label', 'remote_person_uri',
                                    'tags',)
                         }),
        ('Details', {'fields': ('notes', 'page_url', 'file_url', 'isbn', 'zone', 'price')
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
        ISBNField: {'widget': ISBNWidget}
    }

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(ResourceAdmin, self).get_form(request, obj, **kwargs)


