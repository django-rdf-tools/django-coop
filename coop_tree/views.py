# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden
from models import NavNode, NavigableType
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.core.urlresolvers import reverse
import json
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, PermissionDenied
from djaloha.views import process_object_edition
from django.template.loader import select_template
from django.db.models.aggregates import Max
from django.contrib.admin.views.decorators import staff_member_required

class NavTree:
        
    def __init__(self, root_nodes):
        self._nodes = {}
        for node in root_nodes:
            setattr(self, 'node_{0}'.format(node.id), node.label)
            self._nodes[node.id] = node
        self._changed_nodes = []
    
    def __setattr__(self, name, value):
        if hasattr(self, '_changed_nodes') and name.find('node_')==0:
            id = int(name[len('node_'):])
            node = self._nodes[id]
            node.label = value
            self._changed_nodes.append(node)
        self.__dict__[name] = value
    
    def full_clean(self):
        for node in self._changed_nodes:
            node.full_clean()
    
    def save(self):
        for node in self._changed_nodes:
            node.save()
    
    def get_absolute_url(self):
        return reverse('navigation_tree')

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
    tplt = select_template(["tree_content/{0}.html".format(node.content_type), "tree_content/default.html"])
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
    response['message'] = _(u"The node '{0}' has been renamed into '{1}'.").format(old_name, node.label)
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
    node_parent_id = node.parent.id if node.parent else 0
    
    #Update parent if changed
    if node_parent_id != parent_id:
        if parent_id:
            parent_node = NavNode.objects.get(id=parent_id)
        else:
            parent_node = None
        node.parent = parent_node
    
    #Update pos if changed
    if ref_id:
        ref_node = NavNode.objects.get(id=ref_id)
        for next_sibling_node in NavNode.objects.filter(parent=node.parent, ordering__gt=ref_node.ordering):
            next_sibling_node.ordering += 1
            next_sibling_node.save()
        if ref_pos == "before":
            node.ordering = ref_node.ordering
            ref_node.ordering += 1
            ref_node.save()
        elif ref_pos == "after":
            node.ordering = ref_node.ordering + 1
    else:
        node.ordering = NavNode.objects.filter(parent=node.parent).count()+1
    node.save()
    response['message'] = _(u"The node '{0}' has been moved.").format(node.label)
    
    return response

def get_object_label(content_type, object):
    label = ''
    try:
        nt = NavigableType.objects.get(content_type=content_type)
        label = getattr(object, nt.label_field)
    except:
        pass
    if not label:
        try:
            #If the object has get_label use it
            label = object.get_label()
        except Exception, msg:
            #else use cast it to unicode
            label = unicode(object)
    return label

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
    
    #Try to use the label_field of the type if defined
    label = get_object_label(ct, object)
    
    #Create the node
    node = NavNode(label=label)
    #add it as last child of the selected node
    parent_id = request.POST.get('parent_id', 0)
    if parent_id:
        node.parent = NavNode.objects.get(id=parent_id)
        sibling_nodes = NavNode.objects.filter(parent=node.parent)
    else:
        node.parent = None
        sibling_nodes = NavNode.objects.filter(parent__isnull=True)
    max_ordering = sibling_nodes.aggregate(max_ordering=Max('ordering'))['max_ordering'] or 0
    node.ordering = max_ordering + 1
    #associate with a content object
    node.content_type = ct
    node.object_id = object.id
    node.save()
    
    response['label'] = node.label
    response['id'] = 'node_{0}'.format(node.id)
    response['message'] = _(u"'{0}' has added to the navigation tree.").format(label)
    
    return response


def process_nav_edition(request):
    """This handle ajax request sent by the tree component"""
    if request.method == 'POST' and request.is_ajax and request.POST.has_key('msg_id'):
        try:
            supported_msg = {}
            #create a map between message name and handler
            #use the function name as message id
            for fct in (view_navnode, rename_navnode, remove_navnode, move_navnode, add_navnode):
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

def view_tree(request):
    nav_tree = NavTree(NavNode.objects.all())
    
    root_nodes = NavNode.objects.filter(parent__isnull=True).order_by("ordering")
    response = process_nav_edition(request)
    if response:
        return response
    
    response = process_object_edition(request, nav_tree, perm='coop_tree.change_navnode')
    if response:
        return response
    
    nodes_li = u''.join([node.as_li() for node in root_nodes])
    
    nav_types = []
    for nt in NavigableType.objects.all():
        nav_types.append({
            'type': 'type-' + nt.content_type.app_label + '.' + nt.content_type.model,
            'label': nt.content_type.model_class()._meta.verbose_name.capitalize()
        })
    
    return render_to_response(
        'tree.html',
        {'nodes_li': nodes_li, 'object': nav_tree, 'nav_types': nav_types},
        context_instance=RequestContext(request)
    )
    
def edit_node(request, id):
    node = NavNode.objects.get(id=id)
    if node.content_object:
        return HttpResponseRedirect(node.content_object.get_absolute_url())
    raise Http404

@staff_member_required
def get_object_suggest_list(request):
    if not request.is_ajax:
        return Http404
    
    term = request.GET.get("term") #the 1st chars entered in the autocomplete
    
    #the requested content type 
    suggestions = []
    
    #TODO : Get Navigable apps ---------------------------------------
    apps = ('coop_page.page', 'coop_tree.url')
    #-----------------------------------------------------------------
    
    for app_label, model_name in [app.split('.') for app in apps]:
        ct = ContentType.objects.get(app_label=app_label, model=model_name)
        
        #Get the name of the default field for the current type (eg: Page->title, Url->url ...)
        search_field = NavigableType.objects.get(content_type=ct).search_field
        lookup = {search_field+'__icontains': term}
        
        #Get suggestions as a list of {label: object.get_label() or unicode if no get_label, 'value':<object.id>}
        for object in ct.model_class().objects.filter(**lookup):
            suggestions.append({
                'label': get_object_label(ct, object),
                'value': object.id,
                'category': ct.model_class()._meta.verbose_name.capitalize(),
                'type': ct.app_label+u'.'+ct.model,
            })
    
    return HttpResponse(json.dumps(suggestions), mimetype='application/json')    
    