# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden
from coop_cms.models import NavNode, NavType, Article, Image, Document
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.core.urlresolvers import reverse
import json
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, PermissionDenied
from django.template.loader import select_template
from django.db.models.aggregates import Max
from forms import ArticleForm
from django.contrib.messages.api import error as error_message
from coop_cms.models import get_object_label, create_navigation_node

def view_article(request, url):
    """view the article"""
    if request.user.has_perm('coop_cms.change_article'):
        article = get_object_or_404(Article, slug=url) #Draft & Published
    else:
        article = get_object_or_404(Article, slug=url, publication=Article.PUBLISHED) #Published only
    context_dict = {
        'editable': True, 'edit_mode': False, 'article': article, 'draft': article.publication==Article.DRAFT}
    return render_to_response(
        'coop_cms/article.html',
        context_dict,
        context_instance=RequestContext(request)
    )

def edit_article(request, url):
    """edit the article"""
    if not request.user.has_perm('coop_cms.change_article'):
        raise PermissionDenied
    
    article = get_object_or_404(Article, slug=url) #Draft and Published
    
    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(article.get_absolute_url())
    else:
        form = ArticleForm(instance=article)
    
    context_dict = {
        'form': form,
        'editable': True, 'edit_mode': True, 'title': article.title,
        'draft': article.publication==Article.DRAFT,
        'article': article, 'ARTICLE_PUBLISHED': Article.PUBLISHED
    }
    
    return render_to_response(
        'coop_cms/article_form.html',
        context_dict,
        context_instance=RequestContext(request)
    )


def publish_article(request, url):
    """change the publication status of an article"""
    can_change_article = request.user.has_perm('coop_cms.change_article')
    if not can_change_article:
        raise PermissionDenied
    elif request.method == "POST":
        article = get_object_or_404(Article, slug=url, publication=Article.DRAFT)
        article.publication = Article.PUBLISHED
        article.save()
        return HttpResponseRedirect(article.get_absolute_url())
    raise Http404

def show_media_library(request):
    context = {
        'images': Image.objects.all(),
        'documents': Document.objects.all(),
    }
    return render_to_response('coop_cms/media_library.html', context, RequestContext(request))
    
#navigation tree --------------------------------------------------------------

def view_navnode(request):
    """show info about the node when selected"""
    response = {}

    node_id = request.POST['node_id']
    node = NavNode.objects.get(id=node_id)

    #get the admin url
    app, mod = node.content_type.app_label, node.content_type.model
    admin_url = reverse("admin:{0}_{1}_change".format(app, mod), args=(node.object_id,))
    
    #load and render template for the object
    #try to load the corresponding template and if not found use the default one
    tplt = select_template(["coop_cms/navtree_content/{0}.html".format(node.content_type),
                            "coop_cms/navtree_content/default.html"])
    html = tplt.render(RequestContext(request, {'node': node, "admin_url": admin_url}))
    
    #return data has dictionnary
    response['html'] = html
    response['message'] = _(u"Node content loaded.")
    
    return response

def rename_navnode(request):
    """change the name of a node when renamed in the tree"""
    response = {}
    node_id = request.POST['node_id']
    node = NavNode.objects.get(id=node_id) #get the node
    old_name = node.label #get the old name for success message
    node.label = request.POST['name'] #change the name
    node.save()
    if old_name != node.label:
        response['message'] = _(u"The node '{0}' has been renamed into '{1}'.").format(old_name, node.label)
    else:
        response['message'] = ''
    return response

def remove_navnode(request):
    """delete a node"""
    #Keep multi node processing even if multi select is not allowed
    response = {}
    node_ids = request.POST['node_ids'].split(";")
    for node_id in node_ids:
        NavNode.objects.get(id=node_id).delete()
    if len(node_ids)==1:
        response['message'] = _(u"The node has been removed.")
    else:
        response['message'] = _(u"{0} nodes has been removed.").format(len(node_ids))
    return response

def move_navnode(request):
    """move a node in the tree"""
    response = {}
    
    node_id = request.POST['node_id']
    ref_pos = request.POST['ref_pos']
    parent_id = request.POST.get('parent_id', 0)
    ref_id = request.POST.get('ref_id', 0)
    
    node = NavNode.objects.get(id=node_id)
    
    if parent_id:
        sibling_nodes = NavNode.objects.filter(parent__id=parent_id)
        parent_node = NavNode.objects.get(id=parent_id)
    else:
        sibling_nodes = NavNode.objects.filter(parent__isnull=True)
        parent_node = None
        
    if ref_id:
        ref_node = NavNode.objects.get(id=ref_id)
    else:
        ref_node = None
    
    #Update parent if changed
    if parent_node != node.parent:
        if node.parent:
            ex_siblings = NavNode.objects.filter(parent=node.parent).exclude(id=node.id)
        else:
            ex_siblings = NavNode.objects.filter(parent__isnull=True).exclude(id=node.id)
        
        node.parent = parent_node
        
        #restore exsiblings
        for n in ex_siblings.filter(ordering__gt=node.ordering):
            n.ordering -= 1
            n.save()
        
        #move siblings if inserted
        if ref_node:
            if ref_pos == "before":
                to_be_moved = sibling_nodes.filter(ordering__gte=ref_node.ordering)
                node.ordering = ref_node.ordering
            elif ref_pos == "after":
                to_be_moved = sibling_nodes.filter(ordering__gt=ref_node.ordering)
                node.ordering = ref_node.ordering+1
            for n in to_be_moved:
                n.ordering += 1
                n.save()
            
        else:
            #add at the end
            max_ordering = sibling_nodes.aggregate(max_ordering=Max('ordering'))['max_ordering'] or 0
            node.ordering = max_ordering+1
    
    else:
    
        #Update pos if changed
        if ref_node:
            if ref_node.ordering > node.ordering:
                #move forward
                to_be_moved = sibling_nodes.filter(ordering__lt=ref_node.ordering, ordering__gt=node.ordering)
                for next_sibling_node in to_be_moved:
                    next_sibling_node.ordering -= 1
                    next_sibling_node.save()
                
                if ref_pos == "before":
                    node.ordering = ref_node.ordering - 1
                elif ref_pos == "after":
                    node.ordering = ref_node.ordering
                    ref_node.ordering -= 1
                    ref_node.save()
    
            elif ref_node.ordering < node.ordering:
                #move backward
                to_be_moved = sibling_nodes.filter(ordering__gt=ref_node.ordering, ordering__lt=node.ordering)
                for next_sibling_node in to_be_moved:
                    next_sibling_node.ordering += 1
                    next_sibling_node.save()
    
                if ref_pos == "before":
                    node.ordering = ref_node.ordering
                    ref_node.ordering += 1
                    ref_node.save()
                elif ref_pos == "after":
                    node.ordering = ref_node.ordering + 1
        
        else:
            max_ordering = sibling_nodes.aggregate(max_ordering=Max('ordering'))['max_ordering'] or 0
            node.ordering = max_ordering+1
        
    node.save()
    response['message'] = _(u"The node '{0}' has been moved.").format(node.label)
    
    return response

    
def add_navnode(request):
    """Add a new node"""
    response = {}
    
    #get the type of object
    object_type = request.POST['object_type']
    app_label, model_name = object_type.split('.')
    ct = ContentType.objects.get(app_label=app_label, model=model_name)
    model_class = ct.model_class()
    object_id = request.POST['object_id']
    model_name = model_class._meta.verbose_name
    if not object_id:
        raise ValidationError(_(u"Please choose an existing {0}").format(model_name.lower()))
    try:
        object = model_class.objects.get(id=object_id)
    except model_class.DoesNotExist:
        raise ValidationError(_(u"{0} {1} not found").format(model_class._meta.verbose_name, object_id))
    
    #objects can not be added twice in the navigation tree
    if NavNode.objects.filter(content_type=ct, object_id=object.id).count() > 0:
        raise ValidationError(_(u"The {0} is already in navigation").format(model_class._meta.verbose_name))
    
    #Create the node
    node = create_navigation_node(ct, object, request.POST.get('parent_id', 0))
    
    response['label'] = node.label
    response['id'] = 'node_{0}'.format(node.id)
    response['message'] = _(u"'{0}' has added to the navigation tree.").format(node.label)
    
    return response

def get_suggest_list(request):
    response = {}
    suggestions = []
    term = request.POST["term"]#the 1st chars entered in the autocomplete
    for nt in NavType.objects.all():
        ct = nt.content_type
        if nt.label_rule == NavType.LABEL_USE_SEARCH_FIELD:
            #Get the name of the default field for the current type (eg: Page->title, Url->url ...)
            lookup = {nt.search_field+'__icontains': term}
            objects = ct.model_class().objects.filter(**lookup)
        elif nt.label_rule == NavType.LABEL_USE_GET_LABEL:
            objects = [obj for obj in ct.model_class().objects.all() if term in obj.get_label()]
        else:
            objects = [obj for obj in ct.model_class().objects.all() if term in unicode(obj)]
        already_in_navigation = [node.object_id for node in NavNode.objects.filter(content_type=ct)]
        #Get suggestions as a list of {label: object.get_label() or unicode if no get_label, 'value':<object.id>}
        for object in objects:
            if object.id not in already_in_navigation:
                #Suggest only articles which are not in navigation yet
                suggestions.append({
                    'label': get_object_label(ct, object),
                    'value': object.id,
                    'category': ct.model_class()._meta.verbose_name.capitalize(),
                    'type': ct.app_label+u'.'+ct.model,
                })
    
    response['suggestions'] = suggestions
    return response
    
def navnode_in_navigation(request):
    """toogle the is_visible_flag of a navnode"""
    response = {}
    node_id = request.POST['node_id']
    node = NavNode.objects.get(id=node_id) #get the node
    node.in_navigation = not node.in_navigation
    node.save()
    if node.in_navigation:
        response['message'] = _(u"The node is now in navigation.")
        response['label'] = _(u"Remove from navigation")
        response['icon'] = "in_nav"
    else:
        response['message'] = _(u"The node has been removed of the navigation.")
        response['label'] = _(u"Add to navigation")
        response['icon'] = "out_nav"
    return response
    
def process_nav_edition(request):
    """This handle ajax request sent by the tree component"""
    if request.method == 'POST' and request.is_ajax() and request.POST.has_key('msg_id'):
        try:
            #check permissions
            if not request.user.has_perm('coop_cms.change_navtree'):
                raise PermissionDenied
            
            supported_msg = {}
            #create a map between message name and handler
            #use the function name as message id
            for fct in (view_navnode, rename_navnode, remove_navnode, move_navnode,
                add_navnode, get_suggest_list, navnode_in_navigation):
                supported_msg[fct.__name__] = fct
            
            #Call the handler corresponding to the requested message
            response = supported_msg[request.POST['msg_id']](request)
            
            #If no exception raise: Success
            response['status'] = 'success'
            response.setdefault('message', 'Ok') #if no message defined in response, add something

        except KeyError, msg:
            response = {'status': 'error', 'message': _("Unsupported message {0}").format(msg)}
        except PermissionDenied:
            response = {'status': 'error', 'message': _("You are not allowed to add a node")}
        except ValidationError, ex:
           response = {'status': 'error', 'message': u' - '.join(ex.messages)}
        except Exception, msg:
            print msg
            response = {'status': 'error', 'message': _("An error occured")}
        except:
            response = {'status': 'error', 'message': _("An error occured")}

        #return the result as json object
        return HttpResponse(json.dumps(response), mimetype='application/json')
    raise Http404

