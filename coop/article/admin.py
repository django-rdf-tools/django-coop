
# -*- coding:utf-8 -*-

from django.contrib import admin
from django.conf import settings
from tinymce.widgets import AdminTinyMCE
from django import forms
from sorl.thumbnail.admin import AdminImageMixin
from coop.utils.autocomplete_admin import FkAutocompleteAdmin


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

    class CoopArticleAdmin(ArticleAdmin, FkAutocompleteAdmin, AdminImageMixin):
        form = CoopArticleForm
        change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
        change_list_template = 'admin/article_change_list.html'
        list_filter = ['category']

        list_display = ['logo_list_display', 'title', 'publication', 'headline', 'in_newsletter', 'category']
        list_editable = ['publication', 'in_newsletter', 'headline', 'category']
        list_display_links = ['title']

        readonly_fields = []
        fieldsets = (
            #(_('Navigation'), {'fields': ('navigation_parent',)}),
            ('Edition', {'fields': ('title', 'logo', 'content', 'template', 'organization')}),
            ('Options', {'fields': ('summary', 'category', 'is_homepage', 'in_newsletter')}),
        )
        related_search_fields = {'organization': ('title', 'subtitle', 'description'), }

