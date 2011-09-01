# -*- coding: utf-8 -*-

from django.test import TestCase
from models import Page
import json
from django.contrib.auth.models import User, Permission

class PageTest(TestCase):
    
    def _log_as_editor(self):
        user = User.objects.create_user('toto', 'toto@toto.fr', 'toto')
        
        can_edit_page = Permission.objects.get(content_type__app_label='coop_page', codename='change_page')
        user.user_permissions.add(can_edit_page)
        
        self.client.login(username='toto', password='toto')
        
    def _edit_page(self, url, data, expected_status="success"):
        response = self.client.post(url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, response.status_code)
        result = json.loads(response.content)
        self.assertEqual(expected_status, result["status"])
        return result

    def _check_page(self, page, data):
        page = Page.objects.get(slug=page.slug) #refresh
        for (key, value) in data.items():
            self.assertEqual(getattr(page, key), data[key])
            
    def _check_page_not_changed(self, page, data, initial_data):
        page = Page.objects.get(slug=page.slug) #refresh
        
        for (key, value) in data.items():
            self.assertNotEqual(getattr(page, key), data[key])
            
        for (key, value) in initial_data.items():
            self.assertEqual(getattr(page, key), initial_data[key])

    def test_view_page(self):
        page = Page.objects.create(title="test")
        self.assertEqual(page.slug, 'test')
        response = self.client.get(page.get_absolute_url())
        self.assertEqual(200, response.status_code)
        
    def test_404_ok(self):
        response = self.client.get("/jhjhjkahekhj")
        self.assertEqual(404, response.status_code)
        
    def test_is_navigable(self):
        page = Page.objects.create(title="test")
        self.assertEqual('/test', page.get_absolute_url())

    def test_create_slug(self):
        page = Page.objects.create(title=u"voici l'été")
        self.assertEqual(page.slug, 'voici-lete')
        response = self.client.get(page.get_absolute_url())
        self.assertEqual(200, response.status_code)
        
    def test_edit_page(self):
        page = Page.objects.create(title="test")
        
        data = {"title": 'salut', 'content': 'bonjour!'}
        
        self._log_as_editor()
        for (key, value) in data.items():
            self._edit_page(page.get_absolute_url(), {key: value})
            self._check_page(page, {key: value})
        self._check_page(page, data)
        
        data = {"title": 'bye', 'content': 'au revoir'}
        self._edit_page(page.get_absolute_url(), data)
        self._check_page(page, data)
        
    def test_page_edition_permission(self):
        initial_data = {'title': "test", 'content': "this is my page content"}
        page = Page.objects.create(**initial_data)
        
        data = {"title": 'salut'}
        result = self._edit_page(page.get_absolute_url(), data, 'error')
        self.assertEqual({'title': initial_data['title']} , result["old_values"])
        
        self._check_page_not_changed(page, data, initial_data)
        
        
    def test_page_html_in_title(self):
        initial_data = {'title': "test", 'content': "this is my page content"}
        page = Page.objects.create(**initial_data)
        
        self._log_as_editor()
        data = {"title": "<a href='http://www.google.fr'>Google</a>"}
        result = self._edit_page(page.get_absolute_url(), data, 'error')
        self.assertEqual({'title': initial_data['title']} , result["old_values"])
        
        self._check_page_not_changed(page, data, initial_data)
        
        
    def test_ajax_required_for_page_edition(self):
        initial_data = {'title': "test", 'content': "this is my page content"}
        page = Page.objects.create(**initial_data)
        
        self._log_as_editor()
        data = {"title": u"coucou"}
        response = self.client.post(page.get_absolute_url(), data=data)
        self.assertEqual(200, response.status_code)
        
        self._check_page_not_changed(page, data, initial_data)
        
    def _is_aloha_found(self, response):
        self.assertEqual(200, response.status_code)
        return (response.content.find('aloha/aloha.js')>0)
        
    def test_aloha_loaded(self):
        initial_data = {'title': "test", 'content': "this is my page content"}
        page = Page.objects.create(**initial_data)
        response = self.client.get(page.get_absolute_url())
        self.assertFalse(self._is_aloha_found(response))
        
        response = self.client.get(page.get_absolute_url()+"?mode=view")
        self.assertFalse(self._is_aloha_found(response))
        
        response = self.client.get(page.get_absolute_url()+"?mode=edit")
        self.assertTrue(self._is_aloha_found(response))
        
        self._log_as_editor()
        response = self.client.get(page.get_absolute_url()+"?mode=edit")
        self.assertTrue(self._is_aloha_found(response))
        
    def test_checks_aloah_links(self):
        slugs = ("un", "deux", "trois", "quatre")
        for slug in slugs:
            Page.objects.create(title=slug)
        initial_data = {'title': "test", 'content': "this is my page content"}
        page = Page.objects.create(**initial_data)
        
        self._log_as_editor()
        response = self.client.get(page.get_absolute_url()+"?mode=edit")
        self.assertTrue(self._is_aloha_found(response))
        
        context_slugs = [page.slug for page in response.context['links']]
        for slug in slugs:
            self.assertTrue(slug in context_slugs)
        
        