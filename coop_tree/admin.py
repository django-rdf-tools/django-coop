# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.urlresolvers import reverse
import models
from forms import NavigableTypeForm
admin.site.register(models.Url)

class NavNodeAdmin(admin.ModelAdmin):
    list_display = ["label", 'parent', 'ordering', 'content_type', 'object_id']

admin.site.register(models.NavNode, NavNodeAdmin)


class NavigableTypeAdmin(admin.ModelAdmin):
    form = NavigableTypeForm
    
admin.site.register(models.NavigableType, NavigableTypeAdmin)

class NavTreeAdmin(admin.ModelAdmin):

    def nodes_li(self):
        root_nodes = models.NavNode.objects.filter(parent__isnull=True).order_by("ordering")
        nodes_li = u''.join([node.as_li() for node in root_nodes])
        return nodes_li
    
    def suggest_list_url(self):
        return reverse('object_suggest_list')
        
    def get_absolute_url(self):
        return reverse('navigation_tree')

admin.site.register(models.NavTree, NavTreeAdmin)