# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.template import Template, Context
from coop_local.models import Article
from django.core.exceptions import ValidationError
from rss_sync.models import RssItem, RssSource

class BaseTestCase(TestCase):
    def setUp(self):
        self.sync = None
        self.staff = None
        self.editor = None

    def _log_as_synchro(self):
        if not self.sync:
            self.sync = User.objects.create_user('toto', 'toto@toto.fr', 'toto')
            self.sync.is_staff = True
            can_add_items = Permission.objects.get(content_type__app_label='rss_sync', codename='add_rssitem')
            can_change_items = Permission.objects.get(content_type__app_label='rss_sync', codename='change_rssitem')
            self.sync.user_permissions.add(can_add_items)
            self.sync.user_permissions.add(can_change_items)
            self.sync.save()
        
        self.client.login(username='toto', password='toto')
        
    def _log_as_editor(self):
        if not self.editor:
            self.editor = User.objects.create_user('tata', 'tata@tata.fr', 'tata')
            self.editor.is_staff = True
            can_add_art = Permission.objects.get(content_type__app_label='coop_cms', codename='change_article')
            can_change_art = Permission.objects.get(content_type__app_label='coop_cms', codename='add_article')
            self.editor.user_permissions.add(can_add_art)
            self.editor.user_permissions.add(can_change_art)
            self.editor.save()
        
        self.client.login(username='tata', password='tata')
        
    def _log_as_staff(self):
        if not self.staff:
            self.staff = User.objects.create_user('titi', 'titi@titi.fr', 'titi')
            self.staff.is_staff = True
            self.staff.save()
        
        self.client.login(username='titi', password='titi')

class RssTest(BaseTestCase):

    def _do_test_creatitem_from_source(self, url):
        source = RssSource.objects.create(url=url)
        
        self._log_as_synchro()
        
        url = reverse("rss_sync_collect_rss_items", args=[source.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        
        self.assertTrue(RssItem.objects.filter(source=source).count() > 0)
        for item in RssItem.objects.filter(source=source):
            self.assertTrue(len(item.summary)>0)
            self.assertTrue(len(item.title)>0)
            
    def test_creatitem_from_djangoplanet(self):
        self._do_test_creatitem_from_source("http://www.django-fr.org/planete/rss/")
        
    def test_creatitem_from_blogapidev(self):
        self._do_test_creatitem_from_source("http://www.apidev.fr/blog/rss/")
            
    def test_synchro_url_is_not_rss(self):
        source = RssSource.objects.create(url='http://www.apidev.fr/')
        
        self._log_as_synchro()
        
        url = reverse("rss_sync_collect_rss_items", args=[source.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        
        self.assertEquals(RssItem.objects.filter(source=source).count(), 0)
            
    def test_synchro_not_an_url(self):
        source = RssSource.objects.create(url='toto')
        self._log_as_synchro()
        
        url = reverse("rss_sync_collect_rss_items", args=[source.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        
        self.assertEquals(RssItem.objects.filter(source=source).count(), 0)
        
    def test_creatitem_permission_required(self):
        source = RssSource.objects.create(url='http://www.apidev.fr/blog/rss/')
        
        url = reverse("rss_sync_collect_rss_items", args=[source.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(RssItem.objects.filter(source=source).count() == 0)
        
    def test_creatitem_staff_is_not_enough(self):
        source = RssSource.objects.create(url='http://www.apidev.fr/blog/rss/')
        self._log_as_staff()
        url = reverse("rss_sync_collect_rss_items", args=[source.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(RssItem.objects.filter(source=source).count() == 0)
        
    def test_creatitem_no_source(self):
        self._log_as_synchro()
        url = reverse("rss_sync_collect_rss_items", args=[1])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(RssItem.objects.count() == 0)
                             

class CreateArticleTest(BaseTestCase):
    def test_create_article_from_rssitem(self):
        source = RssSource.objects.create(url='http://www.apidev.fr/blog/rss/')
        item = RssItem.objects.create(title="hey-hey", summary="there is nothing i can say", source=source)
        
        self._log_as_editor()
        
        url = reverse("rss_sync_create_cms_article", args=[item.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        
        art = Article.objects.get(title=item.title)
        self.assertEqual(item.summary, art.content)
        self.assertEqual(art.publication, Article.DRAFT)
        
    def test_create_article_from_rssitem_permission_required(self):
        source = RssSource.objects.create(url='http://www.apidev.fr/blog/rss/')
        item = RssItem.objects.create(title="heyhey", summary="nothing i can say", source=source)
        
        url = reverse("rss_sync_create_cms_article", args=[item.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)
        
        self.assertEqual(0, Article.objects.count())
        
    def test_create_article_from_rssitem_staff_is_not_enough(self):
        source = RssSource.objects.create(url='http://www.apidev.fr/blog/rss/')
        item = RssItem.objects.create(title="heyhey", summary="nothing i can say", source=source)
        
        self._log_as_staff()
        
        url = reverse("rss_sync_create_cms_article", args=[item.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)
        
        self.assertEqual(0, Article.objects.count())
        
    def test_creatie_article_item_not_found(self):
        self._log_as_editor()
        url = reverse("rss_sync_create_cms_article", args=[1])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Article.objects.count() == 0)