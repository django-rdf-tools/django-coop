# -*- coding:utf-8 -*-

from django.contrib import admin
from coop_tag.settings import get_class
#from feincms.admin import tree_editor

# TODO : find a nice generic object widget display
# class TaggedItemInline(admin.StackedInline):
#     model = get_class('taggeditem')


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

