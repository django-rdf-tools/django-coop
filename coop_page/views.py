# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from models import Page
from django.utils.translation import ugettext as _
from djaloha.views import process_object_edition
from django.core.exceptions import ValidationError
import re
from coop_tree.models import NavNode

def view_page(request, url):
    
    page = get_object_or_404(Page, slug=url)
    
    def validate_page(page):
        #remove the <br> added by aloha
        page.title = page.title.replace('<br>', '')
        
        #Make sure that there is no HTML content in the title
        if re.search(u'<(.*)>', page.title):
            raise ValidationError(_(u'HTML content is not allowed in the title'))
    
    response = process_object_edition(request, page, object_validator=validate_page)
    #response = process_object_edition(request, page)
    
    if response:
        return response

    root_nodes = NavNode.objects.filter(parent__isnull=True).order_by("ordering")

    context_dict = {
        'object': page,
        'links': Page.objects.all(),
        'editable': True,
        'edit_mode': request.GET.get('mode', 'view')=='edit',
        'nodes_li': u''.join([node.as_li() for node in root_nodes]),
    }

    return render_to_response(
        'page.html',
        context_dict,
        context_instance=RequestContext(request)
    )


