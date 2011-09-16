# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import Template, Context
from models import Link, NavNode, NavType, Article
import json

class NavigationTest(TestCase):

    def setUp(self):
        self.url_ct = ContentType.objects.get(app_label='coop_cms', model='link')
        NavType.objects.create(content_type=self.url_ct, search_field='url', label_rule=NavType.LABEL_USE_SEARCH_FIELD)
        self.editor = None
        self.staff = None
        self.srv_url = reverse("navigation_tree")

    def _log_as_editor(self):
        if not self.editor:
            self.editor = User.objects.create_user('toto', 'toto@toto.fr', 'toto')
            self.editor.is_staff = True
            can_edit_tree = Permission.objects.get(content_type__app_label='coop_cms', codename='change_navtree')
            self.editor.user_permissions.add(can_edit_tree)
            self.editor.save()
        
        self.client.login(username='toto', password='toto')
        
    def _log_as_staff(self):
        if not self.staff:
            self.staff = User.objects.create_user('titi', 'titi@titi.fr', 'titi')
            self.staff.is_staff = True
            self.staff.save()
        
        self.client.login(username='titi', password='titi')

    def test_view_in_admin(self):
        self._log_as_editor()
        url = reverse("admin:coop_cms_navtree_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_add_node(self):
        link = Link.objects.create(url="http://www.google.fr")
        self._log_as_editor()
        
        data = {
            'msg_id': 'add_navnode',
            'object_type':'coop_cms.link',
            'object_id': link.id,
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['label'], 'http://www.google.fr')
        
        nav_node = NavNode.objects.get(object_id=link.id, content_type=self.url_ct)
        self.assertEqual(nav_node.label, 'http://www.google.fr')
        self.assertEqual(nav_node.content_object, link)
        self.assertEqual(nav_node.parent, None)
        self.assertEqual(nav_node.ordering, 1)
        
        #Add a second node as child
        link2 = Link.objects.create(url="http://www.python.org")
        data['object_id'] = link2.id
        data['parent_id'] = link.id
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['label'], 'http://www.python.org')
        nav_node2 = NavNode.objects.get(object_id=link2.id, content_type=self.url_ct)
        self.assertEqual(nav_node2.label, 'http://www.python.org')
        self.assertEqual(nav_node2.content_object, link2)
        self.assertEqual(nav_node2.parent, nav_node)
        self.assertEqual(nav_node.ordering, 1)
        
    def test_move_node_to_parent(self):
        addrs = ("http://www.google.fr", "http://www.python.org", "http://www.quinode.fr", "http://www.apidev.fr")
        links = [Link.objects.create(url=a) for a in addrs]
        
        nodes = []
        for i, link in enumerate(links):
            nodes.append(NavNode.objects.create(label=link.url, content_object=link, ordering=i+1, parent=None))
        
        self._log_as_editor()
        
        data = {
            'msg_id': 'move_navnode',
            'node_id': nodes[-2].id,
            'parent_id': nodes[0].id,
            'ref_pos': 'after',
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        
        node = NavNode.objects.get(id=nodes[-2].id)
        self.assertEqual(node.parent, nodes[0])
        self.assertEqual(node.ordering, 1)
        
        root_nodes = [node for node in NavNode.objects.filter(parent__isnull=True).order_by("ordering")]
        self.assertEqual(nodes[:-2]+nodes[-1:], root_nodes)
        self.assertEqual([1, 2, 3], [n.ordering for n in root_nodes])
        
    def test_move_node_to_root(self):
        addrs = ("http://www.google.fr", "http://www.python.org", "http://www.toto.fr")
        links = [Link.objects.create(url=a) for a in addrs]
        
        nodes = []
        for i, link in enumerate(links):
            nodes.append(NavNode.objects.create(label=link.url, content_object=link, ordering=i+1, parent=None))
        nodes[1].parent = nodes[0]
        nodes[1].ordering = 1
        nodes[1].save()
        nodes[2].parent = nodes[0]
        nodes[2].ordering = 2
        nodes[2].save()
        
        self._log_as_editor()
        
        #Move after
        data = {
            'msg_id': 'move_navnode',
            'node_id': nodes[1].id,
            'ref_pos': 'after',
            'ref_id': nodes[0].id,            
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        
        node = NavNode.objects.get(id=nodes[1].id)
        self.assertEqual(node.parent, None)
        self.assertEqual(node.ordering, 2)
        self.assertEqual(NavNode.objects.get(id=nodes[0].id).ordering, 1)
        self.assertEqual(NavNode.objects.get(id=nodes[2].id).ordering, 1)
        
        #Move before
        data = {
            'msg_id': 'move_navnode',
            'node_id': nodes[2].id,
            'ref_pos': 'before',
            'ref_id': nodes[0].id,
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        if result['status'] != 'success':
            print result['message']
        self.assertEqual(result['status'], 'success')
        
        node = NavNode.objects.get(id=nodes[2].id)
        self.assertEqual(node.parent, None)
        self.assertEqual(node.ordering, 1)
        self.assertEqual(NavNode.objects.get(id=nodes[0].id).ordering, 2)
        self.assertEqual(NavNode.objects.get(id=nodes[1].id).ordering, 3)
        
    def test_move_same_level(self):
        addrs = ("http://www.google.fr", "http://www.python.org", "http://www.quinode.fr", "http://www.apidev.fr")
        links = [Link.objects.create(url=a) for a in addrs]
        
        nodes = []
        for i, link in enumerate(links):
            nodes.append(NavNode.objects.create(label=link.url, content_object=link, ordering=i+1, parent=None))
        
        self._log_as_editor()
        
        #Move the 4th just after the 1st one
        data = {
            'msg_id': 'move_navnode',
            'node_id': nodes[-2].id,
            'ref_id': nodes[0].id,
            'ref_pos': 'after',
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        
        nodes = [NavNode.objects.get(id=n.id) for n in nodes]#refresh
        [self.assertEqual(n.parent, None) for n in nodes]
        self.assertEqual([1, 3, 2, 4], [n.ordering for n in nodes])
        
        #Move the 1st before the 4th
        data = {
            'msg_id': 'move_navnode',
            'node_id': nodes[0].id,
            'ref_id': nodes[-1].id,
            'ref_pos': 'before',
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        
        nodes = [NavNode.objects.get(id=n.id) for n in nodes]#refresh
        [self.assertEqual(n.parent, None) for n in nodes]
        self.assertEqual([3, 2, 1, 4], [n.ordering for n in nodes])
        
    def test_delete_node(self):
        addrs = ("http://www.google.fr", "http://www.python.org", "http://www.quinode.fr", "http://www.apidev.fr")
        links = [Link.objects.create(url=a) for a in addrs]
        
        nodes = []
        for i, link in enumerate(links):
            nodes.append(NavNode.objects.create(label=link.url, content_object=link, ordering=i+1, parent=None))
        
        self._log_as_editor()
        
        #remove the 2ns one
        data = {
            'msg_id': 'remove_navnode',
            'node_ids': nodes[1].id,
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
    
        nodes_after = NavNode.objects.all().order_by('ordering')
        self.assertEqual(3, len(nodes_after))
        self.assertTrue(nodes[1] not in nodes_after)
        for i, node in enumerate(nodes_after):
            self.assertTrue(node in nodes)
            self.assertTrue(i+1, node.ordering)
            
    def test_delete_node_and_children(self):
        addrs = ("http://www.google.fr", "http://www.python.org", "http://www.quinode.fr", "http://www.apidev.fr")
        links = [Link.objects.create(url=a) for a in addrs]
        
        nodes = []
        for i, link in enumerate(links):
            nodes.append(NavNode.objects.create(label=link.url, content_object=link, ordering=i+1, parent=None))
        
        nodes[-1].parent = nodes[-2]
        nodes[-1].ordering = 1
        nodes[-1].save()
        
        self._log_as_editor()
        
        #remove the 2ns one
        data = {
            'msg_id': 'remove_navnode',
            'node_ids': nodes[-2].id,
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
    
        nodes_after = NavNode.objects.all().order_by('ordering')
        self.assertEqual(2, len(nodes_after))
        self.assertTrue(nodes[-1] not in nodes_after)
        self.assertTrue(nodes[-2] not in nodes_after)
        for i, node in enumerate(nodes_after):
            self.assertTrue(node in nodes)
            self.assertTrue(i+1, node.ordering)
            
    def test_rename_node(self):
        addrs = ("http://www.google.fr", "http://www.python.org", "http://www.quinode.fr", "http://www.apidev.fr")
        links = [Link.objects.create(url=a) for a in addrs]
        
        nodes = []
        for i, link in enumerate(links):
            nodes.append(NavNode.objects.create(label=link.url, content_object=link, ordering=i+1, parent=None))
        
        self._log_as_editor()
        
        #rename the 1st one
        data = {
            'msg_id': 'rename_navnode',
            'node_id': nodes[0].id,
            'name': 'Google',
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
    
        node = NavNode.objects.get(id=nodes[0].id)
        self.assertEqual(data["name"], node.label)
        self.assertEqual(links[0].url, node.content_object.url)#object not renamed
        
        for n in nodes[1:]:
            node = NavNode.objects.get(id=n.id)
            self.assertEqual(n.label, node.label)
        
    def test_view_node(self):
        addrs = ("http://www.google.fr", "http://www.python.org", "http://www.quinode.fr", "http://www.apidev.fr")
        links = [Link.objects.create(url=a) for a in addrs]
        
        nodes = []
        for i, link in enumerate(links):
            nodes.append(NavNode.objects.create(label=link.url, content_object=link, ordering=i+1, parent=None))
        
        self._log_as_editor()
        
        #remove the 2ns one
        data = {
            'msg_id': 'view_navnode',
            'node_id': nodes[0].id,
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['html'].find(nodes[0].get_absolute_url())>=0)
        self.assertTrue(result['html'].find(nodes[1].get_absolute_url())<0)
        self.assertTemplateUsed(response, 'coop_cms/navtree_content/default.html')
        
    def _do_test_get_suggest_list(self):
        addrs = ("http://www.google.fr", "http://www.python.org", "http://www.quinode.fr", "http://www.apidev.fr")
        links = [Link.objects.create(url=a) for a in addrs]
        
        nodes = []
        for i, link in enumerate(links):
            nodes.append(NavNode.objects.create(label=link.url, content_object=link, ordering=i+1, parent=None))
        
        self._log_as_editor()
        
        data = {
            'msg_id': 'get_suggest_list',
            'term': '.fr'
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(result['suggestions']), 3)
        
    def test_get_suggest_list(self):
        self._do_test_get_suggest_list()
        
    def test_get_suggest_list_get_label(self):
        
        nt = NavType.objects.get(content_type=self.url_ct)
        nt.search_field = ''
        nt.label_rule=NavType.LABEL_USE_GET_LABEL
        nt.save()
        self._do_test_get_suggest_list()
        
    def test_get_suggest_list_unicode(self):
        
        nt = NavType.objects.get(content_type=self.url_ct)
        nt.search_field = ''
        nt.label_rule=NavType.LABEL_USE_UNICODE
        nt.save()
        self._do_test_get_suggest_list()
        
        
    def test_unknow_message(self):
        self._log_as_editor()
        
        data = {
            'msg_id': 'oups',
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'error')
        
    def test_missing_message(self):
        self._log_as_editor()
        
        data = {
        }
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)
        
    def test_not_ajax(self):
        link = Link.objects.create(url="http://www.google.fr")
        self._log_as_editor()
        
        data = {
            'msg_id': 'add_navnode',
            'object_type':'coop_cms.link',
            'object_id': link.id,
        }
        
        response = self.client.post(self.srv_url, data=data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(0, NavNode.objects.count())
        
    def test_add_unknown_obj(self):
        self._log_as_editor()
        
        data = {
            'msg_id': 'add_navnode',
            'object_type':'coop_cms.link',
            'object_id': 11,
        }
        
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(0, NavNode.objects.count())
        
    def test_remove_unknown_node(self):
        self._log_as_editor()
        
        data = {
            'msg_id': 'remove_navnode',
            'node_ids': 11,
        }
        
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'error')
        
    def test_rename_unknown_node(self):
        self._log_as_editor()
        
        data = {
            'msg_id': 'remove_navnode',
            'node_id': 11,
            'label': 'oups'
        }
        
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'error')
        
    def test_check_auth(self):
        link = Link.objects.create(url='http://www.google.fr')
        node = NavNode.objects.create(label=link.url, content_object=link, ordering=1, parent=None)

        data = {
            'node_id': node.id,
            'node_ids': node.id,
            'ref_pos': 'after',
            'name': 'oups',
            'term': 'goo',
            'object_type':'coop_cms.link',
            'object_id': link.id,
        }
        
        for msg_id in ('add_navnode', 'move_navnode', 'rename_navnode', 'get_suggest_list', 'view_navnode', 'remove_navnode'):
            data['msg_id'] = msg_id
            
            self._log_as_staff()
            response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200)
            result = json.loads(response.content)
            self.assertEqual(result['status'], 'error')
            
            self._log_as_editor()
            response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200)
            result = json.loads(response.content)
            self.assertEqual(result['status'], 'success')
            
    def test_set_out_of_nav(self):
        self._log_as_editor()
        
        link = Link.objects.create(url='http://www.google.fr')
        node = NavNode.objects.create(label=link.url, content_object=link, ordering=1, parent=None, in_navigation=True)
        
        data = {
            'msg_id': 'navnode_in_navigation',
            'node_id': node.id,
        }
        
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        self.assertNotEqual(result['message'], '')
        self.assertEqual(result['icon'], 'out_nav')
        node = NavNode.objects.get(id=node.id)
        self.assertFalse(node.in_navigation)
        
    def test_set_in_nav(self):
        self._log_as_editor()
        
        link = Link.objects.create(url='http://www.google.fr')
        node = NavNode.objects.create(label=link.url, content_object=link, ordering=1, parent=None, in_navigation=False)
        
        data = {
            'msg_id': 'navnode_in_navigation',
            'node_id': node.id,
        }
        
        response = self.client.post(self.srv_url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        self.assertNotEqual(result['message'], '')
        self.assertEqual(result['icon'], 'in_nav')
        node = NavNode.objects.get(id=node.id)
        self.assertTrue(node.in_navigation)
        
            
class TemplateTagsTest(TestCase):
    
    def setUp(self):
        link1 = Link.objects.create(url='http://www.google.fr')
        link2 = Link.objects.create(url='http://www.python.org')
        link3 = Link.objects.create(url='http://www.quinode.fr')
        link4 = Link.objects.create(url='http://www.apidev.fr')
        link5 = Link.objects.create(url='http://www.toto.fr')
        link6 = Link.objects.create(url='http://www.titi.fr')
        
        self.nodes = []
        
        self.nodes.append(NavNode.objects.create(label=link1.url, content_object=link1, ordering=1, parent=None))
        self.nodes.append(NavNode.objects.create(label=link2.url, content_object=link2, ordering=2, parent=None))
        self.nodes.append(NavNode.objects.create(label=link3.url, content_object=link3, ordering=3, parent=None))
        self.nodes.append(NavNode.objects.create(label=link4.url, content_object=link4, ordering=1, parent=self.nodes[2]))
        self.nodes.append(NavNode.objects.create(label=link5.url, content_object=link5, ordering=1, parent=self.nodes[3]))
        self.nodes.append(NavNode.objects.create(label=link6.url, content_object=link6, ordering=2, parent=self.nodes[3]))
        
    def test_view_navigation(self):
        tpl = Template('{% load coop_navigation %}{%navigation_as_nested_ul%}')
        html = tpl.render(Context({}))
        
        positions = [html.find('{0}'.format(n.content_object.url)) for n in self.nodes]
        for pos in positions:
            self.assertTrue(pos>=0)
        sorted_positions = positions[:]
        sorted_positions.sort()
        self.assertEqual(positions, sorted_positions)
        
    def _insert_new_node(self):
        link7 = Link.objects.create(url='http://www.tutu.fr')
        self.nodes.insert(-1, NavNode.objects.create(label=link7.url, content_object=link7, ordering=2, parent=self.nodes[3]))
        self.nodes[-1].ordering = 3
        self.nodes[-1].save()
        
    def test_view_navigation_order(self):
        self._insert_new_node()
        
        tpl = Template('{% load coop_navigation %}{%navigation_as_nested_ul%}')
        html = tpl.render(Context({}))
        
        positions = [html.find('{0}'.format(n.content_object.url)) for n in self.nodes]
        for pos in positions:
            self.assertTrue(pos>=0)
        sorted_positions = positions[:]
        sorted_positions.sort()
        self.assertEqual(positions, sorted_positions)
            
    def test_view_out_of_navigation(self):
        self.nodes[2].in_navigation = False
        self.nodes[2].save()
        
        tpl = Template('{% load coop_navigation %}{%navigation_as_nested_ul%}')
        html = tpl.render(Context({}))
        
        for n in self.nodes[:2]:
            self.assertTrue(html.find('{0}'.format(n.content_object.url))>=0)
            
        for n in self.nodes[2:]:
            self.assertFalse(html.find('{0}'.format(n.content_object.url))>=0)
            
    def test_view_navigation_custom_template(self):
        cst_tpl = Template('<span id="{{node.id}}">{{node.label}}</span>')
        tpl = Template('{% load coop_navigation %}{%navigation_as_nested_ul li_template=cst_tpl%}')
        
        html = tpl.render(Context({'cst_tpl': cst_tpl}))
        
        for n in self.nodes:
            self.assertTrue(html.find(u'<span id="{0.id}">{0.label}</span>'.format(n))>=0)
            self.assertFalse(html.find('<a href="{0}">{1}</a>'.format(n.content_object.url, n.label))>=0)
            
    def test_view_navigation_custom_template_file(self):
        tpl = Template('{% load coop_navigation %}{%navigation_as_nested_ul li_template=coop_cms/test_li.html%}')
        
        html = tpl.render(Context({}))
        
        for n in self.nodes:
            self.assertTrue(html.find(u'<span id="{0.id}">{0.label}</span>'.format(n))>=0)
            self.assertFalse(html.find('<a href="{0}">{1}</a>'.format(n.content_object.url, n.label))>=0)
            
    def test_view_navigation_css(self):
        tpl = Template('{% load coop_navigation %}{%navigation_as_nested_ul css_class=toto%}')
        html = tpl.render(Context({}))
        self.assertTrue(html.count('<li class="toto">'), len(self.nodes))
        
    def test_view_navigation_custom_template_and_css(self):
        tpl = Template(
            '{% load coop_navigation %}{%navigation_as_nested_ul li_template=coop_cms/test_li.html css_class=toto%}'
        )
        html = tpl.render(Context({}))
        self.assertTrue(html.count('<li class="toto">'), len(self.nodes))
            
        for n in self.nodes:
            self.assertTrue(html.find(u'<span id="{0.id}">{0.label}</span>'.format(n))>=0)
            self.assertFalse(html.find('<a href="{0}">{1}</a>'.format(n.content_object.url, n.label))>=0)
            
    def test_view_breadcrumb(self):
        tpl = Template('{% load coop_navigation %}{% navigation_breadcrumb obj %}')
        html = tpl.render(Context({'obj': self.nodes[5].content_object}))
        
        for n in (self.nodes[2], self.nodes[3], self.nodes[5]) :
            self.assertTrue(html.find('{0}'.format(n.content_object.url))>=0)
            
        for n in (self.nodes[0], self.nodes[1], self.nodes[4]) :
            self.assertFalse(html.find('{0}'.format(n.content_object.url))>=0)
            
    def test_view_breadcrumb_out_of_navigation(self):
        for n in self.nodes:
            n.in_navigation = False
            n.save()
        
        tpl = Template('{% load coop_navigation %}{% navigation_breadcrumb obj %}')
        html = tpl.render(Context({'obj': self.nodes[5].content_object}))
        
        for n in (self.nodes[2], self.nodes[3], self.nodes[5]) :
            self.assertTrue(html.find('{0}'.format(n.content_object.url))>=0)
            
        for n in (self.nodes[0], self.nodes[1], self.nodes[4]) :
            self.assertFalse(html.find('{0}'.format(n.content_object.url))>=0)

    def test_view_breadcrumb_custom_template(self):
        cst_tpl = Template('<span id="{{node.id}}">{{node.label}}</span>')
        tpl = Template('{% load coop_navigation %}{% navigation_breadcrumb obj li_template=cst_tpl%}')
        
        html = tpl.render(Context({'obj': self.nodes[5].content_object, 'cst_tpl': cst_tpl}))
        
        for n in (self.nodes[2], self.nodes[3], self.nodes[5]) :
            self.assertTrue(html.find(u'<span id="{0.id}">{0.label}</span>'.format(n))>=0)
            self.assertFalse(html.find('<a href="{0}">{1}</a>'.format(n.content_object.url, n.label))>=0)
            
    def test_view_breadcrumb_custom_template_file(self):
        tpl = Template('{% load coop_navigation %}{% navigation_breadcrumb obj li_template=coop_cms/test_li.html%}')
        
        html = tpl.render(Context({'obj': self.nodes[5].content_object}))
        
        for n in (self.nodes[2], self.nodes[3], self.nodes[5]) :
            self.assertTrue(html.find(u'<span id="{0.id}">{0.label}</span>'.format(n))>=0)
            self.assertFalse(html.find('<a href="{0}">{1}</a>'.format(n.content_object.url, n.label))>=0)
            
    def test_view_children(self):
        tpl = Template('{% load coop_navigation %}{%navigation_children obj %}')
        html = tpl.render(Context({'obj': self.nodes[3].content_object}))
        
        for n in self.nodes[4:]:
            self.assertTrue(html.find(n.content_object.url)>=0)
            
        for n in self.nodes[:4]:
            self.assertFalse(html.find('{0}'.format(n.content_object.url))>=0)
            
    def test_view_children_out_of_navigation(self):
        self.nodes[1].in_navigation = False
        self.nodes[1].save()
        
        self.nodes[5].in_navigation = False
        self.nodes[5].save()
        
        tpl = Template('{% load coop_navigation %}{%navigation_children obj %}')
        html = tpl.render(Context({'obj': self.nodes[3].content_object}))
        
        for n in (self.nodes[4], ):
            self.assertTrue(html.find(n.content_object.url)>=0)
            
        for n in self.nodes[:4] + [self.nodes[5]]:
            self.assertFalse(html.find('{0}'.format(n.content_object.url))>=0)
            
    def test_view_children_custom_template(self):
        cst_tpl = Template('<span id="{{node.id}}">{{node.label}}</span>')
        tpl = Template('{% load coop_navigation %}{%navigation_children obj  li_template=cst_tpl %}')
        html = tpl.render(Context({'obj': self.nodes[3].content_object, 'cst_tpl': cst_tpl}))
        
        for n in self.nodes[4:]:
            self.assertTrue(html.find(u'<span id="{0.id}">{0.label}</span>'.format(n))>=0)
            self.assertFalse(html.find('<a href="{0}">{1}</a>'.format(n.content_object.url, n.label))>=0)
            
    def test_view_children_custom_template_file(self):
        tpl = Template('{% load coop_navigation %}{%navigation_children obj li_template=coop_cms/test_li.html %}')
        html = tpl.render(Context({'obj': self.nodes[3].content_object}))
        
        for n in self.nodes[4:]:
            self.assertTrue(html.find(u'<span id="{0.id}">{0.label}</span>'.format(n))>=0)
            self.assertFalse(html.find('<a href="{0}">{1}</a>'.format(n.content_object.url, n.label))>=0)
            
    def test_view_children_order(self):
        self._insert_new_node()
        nodes = self.nodes[3].get_children(in_navigation=True)
        tpl = Template('{% load coop_navigation %}{%navigation_children obj%}')
        html = tpl.render(Context({'obj': self.nodes[3].content_object}))
        positions = [html.find(n.content_object.url) for n in nodes]
        for pos in positions:
            self.assertTrue(pos>=0)
        sorted_positions = positions[:]
        sorted_positions.sort()
        self.assertEqual(positions, sorted_positions)
            
    def test_view_siblings(self):
        tpl = Template('{% load coop_navigation %}{% navigation_siblings obj %}')
        html = tpl.render(Context({'obj': self.nodes[0].content_object}))
        for n in self.nodes[:3]:
            self.assertTrue(html.find('{0}'.format(n.content_object.url))>=0)
            
        for n in self.nodes[3:]:
            self.assertFalse(html.find('{0}'.format(n.content_object.url))>=0)
    
    def test_view_siblings_order(self):
        self._insert_new_node()
        all_nodes = [n for n in self.nodes]
        nodes = all_nodes[-1].get_siblings(in_navigation=True)
        tpl = Template('{% load coop_navigation %}{%navigation_siblings obj%}')
        html = tpl.render(Context({'obj': all_nodes[-1].content_object}))
        positions = [html.find(n.content_object.url) for n in nodes]
        for pos in positions:
            self.assertTrue(pos>=0)
        sorted_positions = positions[:]
        sorted_positions.sort()
        self.assertEqual(positions, sorted_positions)
            
    def test_view_siblings_out_of_navigation(self):
        self.nodes[2].in_navigation = False
        self.nodes[2].save()
        
        self.nodes[5].in_navigation = False
        self.nodes[5].save()
        
        tpl = Template('{% load coop_navigation %}{% navigation_siblings obj %}')
        html = tpl.render(Context({'obj': self.nodes[0].content_object}))
        
        for n in self.nodes[:2]:
            self.assertTrue(html.find('{0}'.format(n.content_object.url))>=0)
            
        for n in self.nodes[2:]:
            self.assertFalse(html.find('{0}'.format(n.content_object.url))>=0)
    
    def test_view_siblings_custom_template(self):
        cst_tpl = Template('<span id="{{node.id}}">{{node.label}}</span>')
        tpl = Template('{% load coop_navigation %}{% navigation_siblings obj li_template=cst_tpl%}')
        html = tpl.render(Context({'obj': self.nodes[0].content_object, 'cst_tpl': cst_tpl}))
        
        for n in self.nodes[:3]:
            self.assertTrue(html.find(u'<span id="{0.id}">{0.label}</span>'.format(n))>=0)
            self.assertFalse(html.find('<a href="{0}">{1}</a>'.format(n.content_object.url, n.label))>=0)
            
    def test_view_siblings_custom_template_file(self):
        tpl = Template('{% load coop_navigation %}{% navigation_siblings obj li_template=coop_cms/test_li.html%}')
        html = tpl.render(Context({'obj': self.nodes[0].content_object}))
        
        for n in self.nodes[:3]:
            self.assertTrue(html.find(u'<span id="{0.id}">{0.label}</span>'.format(n))>=0)
            self.assertFalse(html.find('<a href="{0}">{1}</a>'.format(n.content_object.url, n.label))>=0)
            
    def test_navigation_no_nodes(self):
        NavNode.objects.all().delete()
        tpl = Template('{% load coop_navigation %}{%navigation_as_nested_ul%}')
        html = tpl.render(Context({})).replace(' ', '')
        self.assertEqual(html, '')
            
    def test_breadcrumb_no_nodes(self):
        NavNode.objects.all().delete()
        link = Link.objects.get(url='http://www.python.org')
        tpl = Template('{% load coop_navigation %}{% navigation_breadcrumb obj %}')
        html = tpl.render(Context({'obj': link})).replace(' ', '')
        self.assertEqual(html, '')
            
    def test_children_no_nodes(self):
        NavNode.objects.all().delete()
        link = Link.objects.get(url='http://www.python.org')
        tpl = Template('{% load coop_navigation %}{%navigation_children obj %}')
        html = tpl.render(Context({'obj': link })).replace(' ', '')
        self.assertEqual(html, '')
            
    def test_siblings_no_nodes(self):
        NavNode.objects.all().delete()
        link = Link.objects.get(url='http://www.python.org')
        tpl = Template('{% load coop_navigation %}{% navigation_siblings obj %}')
        html = tpl.render(Context({'obj': link})).replace(' ', '')
        self.assertEqual(html, '')
        

class ArticleTest(TestCase):
    
    def _log_as_editor(self):
        user = User.objects.create_user('toto', 'toto@toto.fr', 'toto')
        
        can_edit_article = Permission.objects.get(content_type__app_label='coop_cms', codename='change_article')
        user.user_permissions.add(can_edit_article)
        
        self.client.login(username='toto', password='toto')
        
    def _edit_article(self, url, data, expected_status="success"):
        response = self.client.post(url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, response.status_code)
        result = json.loads(response.content)
        self.assertEqual(expected_status, result["status"])
        return result

    def _check_article(self, article, data):
        article = Article.objects.get(slug=article.slug) #refresh
        for (key, value) in data.items():
            self.assertEqual(getattr(article, key), data[key])
            
    def _check_article_not_changed(self, article, data, initial_data):
        article = Article.objects.get(slug=article.slug) #refresh
        
        for (key, value) in data.items():
            self.assertNotEqual(getattr(article, key), data[key])
            
        for (key, value) in initial_data.items():
            self.assertEqual(getattr(article, key), initial_data[key])

    def test_view_article(self):
        article = Article.objects.create(title="test")
        self.assertEqual(article.slug, 'test')
        response = self.client.get(article.get_absolute_url())
        self.assertEqual(200, response.status_code)
        
    def test_404_ok(self):
        response = self.client.get("/jhjhjkahekhj")
        self.assertEqual(404, response.status_code)
        
    def test_is_navigable(self):
        article = Article.objects.create(title="test")
        self.assertEqual('/test', article.get_absolute_url())

    def test_create_slug(self):
        article = Article.objects.create(title=u"voici l'été")
        self.assertEqual(article.slug, 'voici-lete')
        response = self.client.get(article.get_absolute_url())
        self.assertEqual(200, response.status_code)
        
    def test_edit_article(self):
        article = Article.objects.create(title="test")
        
        data = {"title": 'salut', 'content': 'bonjour!'}
        
        self._log_as_editor()
        for (key, value) in data.items():
            self._edit_article(article.get_absolute_url(), {key: value})
            self._check_article(article, {key: value})
        self._check_article(article, data)
        
        data = {"title": 'bye', 'content': 'au revoir'}
        self._edit_article(article.get_absolute_url(), data)
        self._check_article(article, data)
        
    def test_article_edition_permission(self):
        initial_data = {'title': "test", 'content': "this is my article content"}
        article = Article.objects.create(**initial_data)
        
        data = {"title": 'salut'}
        result = self._edit_article(article.get_absolute_url(), data, 'error')
        self.assertEqual({'title': initial_data['title']} , result["old_values"])
        
        self._check_article_not_changed(article, data, initial_data)
        
        
    def test_article_html_in_title(self):
        initial_data = {'title': "test", 'content': "this is my article content"}
        article = Article.objects.create(**initial_data)
        
        self._log_as_editor()
        data = {"title": "<a href='http://www.google.fr'>Google</a>"}
        result = self._edit_article(article.get_absolute_url(), data, 'error')
        self.assertEqual({'title': initial_data['title']} , result["old_values"])
        
        self._check_article_not_changed(article, data, initial_data)
        
        
    def test_ajax_required_for_article_edition(self):
        initial_data = {'title': "test", 'content': "this is my article content"}
        article = Article.objects.create(**initial_data)
        
        self._log_as_editor()
        data = {"title": u"coucou"}
        response = self.client.post(article.get_absolute_url(), data=data)
        self.assertEqual(200, response.status_code)
        
        self._check_article_not_changed(article, data, initial_data)
        
    def _is_aloha_found(self, response):
        self.assertEqual(200, response.status_code)
        return (response.content.find('aloha/aloha.js')>0)
        
    def test_aloha_loaded(self):
        initial_data = {'title': "test", 'content': "this is my article content"}
        article = Article.objects.create(**initial_data)
        response = self.client.get(article.get_absolute_url())
        self.assertFalse(self._is_aloha_found(response))
        
        response = self.client.get(article.get_absolute_url()+"?mode=view")
        self.assertFalse(self._is_aloha_found(response))
        
        response = self.client.get(article.get_absolute_url()+"?mode=edit")
        self.assertTrue(self._is_aloha_found(response))
        
        self._log_as_editor()
        response = self.client.get(article.get_absolute_url()+"?mode=edit")
        self.assertTrue(self._is_aloha_found(response))
        
    def test_checks_aloah_links(self):
        slugs = ("un", "deux", "trois", "quatre")
        for slug in slugs:
            Article.objects.create(title=slug)
        initial_data = {'title': "test", 'content': "this is my article content"}
        article = Article.objects.create(**initial_data)
        
        self._log_as_editor()
        response = self.client.get(article.get_absolute_url()+"?mode=edit")
        self.assertTrue(self._is_aloha_found(response))
        
        context_slugs = [article.slug for article in response.context['links']]
        for slug in slugs:
            self.assertTrue(slug in context_slugs)
        
        