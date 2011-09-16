# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.urlresolvers import reverse
import models
from forms import NavTypeForm

class NavNodeAdmin(admin.ModelAdmin):
    list_display = ["label", 'parent', 'ordering', 'in_navigation', 'content_type', 'object_id']

admin.site.register(models.NavNode, NavNodeAdmin)


class NavTypeAdmin(admin.ModelAdmin):
    form = NavTypeForm
    
admin.site.register(models.NavType, NavTypeAdmin)

class NavTreeAdmin(admin.ModelAdmin):

    def nodes_li(self):
        root_nodes = models.NavNode.objects.filter(parent__isnull=True).order_by("ordering")
        nodes_li = u''.join([node.as_jstree() for node in root_nodes])
        return nodes_li
    
    def suggest_list_url(self):
        return reverse('object_suggest_list')
        
    def get_absolute_url(self):
        return reverse('navigation_tree')

admin.site.register(models.NavTree, NavTreeAdmin)

admin.site.register(models.Article)
admin.site.register(models.Link)