# -*- coding:utf-8 -*-

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from django.test.client import Client
from django.db.models import get_app, get_models
from django.conf import settings
from django.contrib import admin

class AdminTest(TestCase):

    fixtures = ['tests/users.json']


    def test_site(self):
        response = self.client.get('/admin/', follow=True)
        self.assertEqual(response.status_code,200, 'check /admin/ without user')

        response = self.client.get('/')
        self.assertEqual(response.status_code,200)


    def test_admin(self):
        self.client.login(username='clo',password='clo')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code,200)

        app_name = 'coop_local'
        app = get_app(app_name)
        registered = admin.site._registry
        for m in get_models(app):
            if m in registered:
                url = '/admin/%s/%s/' % (app_name,  m.__name__.lower())
                # print 'test url %s' % url
                response = self.client.get(url, follow=True)
                self.assertEqual(response.status_code,200, "check url %s" % url)







