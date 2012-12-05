
# -*- coding:utf-8 -*-

from django.contrib import admin
from django.conf import settings
from tinymce.widgets import AdminTinyMCE
from django import forms
from sorl.thumbnail.admin import AdminImageMixin
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, NoLookupsFkAutocompleteAdmin
from django.db.models.loading import get_model
from chosen import widgets as chosenwidgets

if "coop.agenda" in settings.INSTALLED_APPS:
    from coop.agenda.admin import DatedInline

if "coop_cms" in settings.INSTALLED_APPS:
    from coop_cms.admin import NavTreeAdmin, ArticleAdmin
    from coop_cms.settings import get_article_class, get_navTree_class
    from coop_cms.forms import ArticleAdminForm

    # -- We need to customize coop-cms NavtreeAdmin

    class MyNavTreeAdmin(NavTreeAdmin):
        change_form_template = 'admin/navtree_change_form.html'

    navtree_model = get_navTree_class()
    admin.site.unregister(navtree_model)
    admin.site.register(navtree_model, MyNavTreeAdmin)

    # -- We need to customize coop-cms ArticleAdmin

    class CoopArticleForm(ArticleAdminForm):
        content = forms.CharField(widget=AdminTinyMCE(attrs={'cols': 80, 'rows': 60}), required=False)

        class Meta:
            model = get_model('coop_local', 'Article')
            widgets = {'sites': chosenwidgets.ChosenSelectMultiple()}

        def __init__(self, *args, **kwargs):
            super(CoopArticleForm, self).__init__(*args, **kwargs)
            if 'sites' in self.fields:
                self.fields['sites'].help_text = None
        #     from django.forms.widgets import HiddenInput
        #     self.fields['remote_organization_uri'].widget = HiddenInput()
        #     self.fields['remote_person_uri'].widget = HiddenInput()


    class CoopArticleAdmin(ArticleAdmin, NoLookupsFkAutocompleteAdmin, AdminImageMixin):
        form = CoopArticleForm
        change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
        change_list_template = 'admin/article_change_list.html'
        list_filter = ['category']
        search_fields = ['title', 'summary', 'content']
        ordering = ['-created']

        list_display = ['logo_list_display', 'title', 'publication', 'headline', 'isSection', 'category']
        list_editable = ['publication', 'isSection', 'headline', 'category']
        list_display_links = ['title']

        readonly_fields = []
        fieldsets = (
            #(_('Navigation'), {'fields': ('navigation_parent',)}),
            ('Edition', {'fields': ['title', 'logo', 'content', 
                                    'organization', 'remote_organization_label', 'remote_organization_uri',
                                    'person', 'remote_person_label', 'remote_person_uri']}),
            ('Options', {'fields': ('summary', 'category', 'template', 'is_homepage', 'in_newsletter', 'isSection')}),
        )
        related_search_fields = {'organization': ('title', 'subtitle', 'description'), 
                                 'person': ('first_name', 'last_name',), }

        if "coop.agenda" in settings.INSTALLED_APPS:
            inlines = [DatedInline]

        if settings.COOP_USE_SITES:
            fieldsets[0][1]['fields'].insert(0, 'sites')


