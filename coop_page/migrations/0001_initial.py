# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Page'
        db.create_table('coop_page_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, unique=True, max_length=100, blank=True)),
            ('title', self.gf('django.db.models.fields.TextField')(default=u'Page title')),
            ('content', self.gf('django.db.models.fields.TextField')(default=u'Page content')),
        ))
        db.send_create_signal('coop_page', ['Page'])


    def backwards(self, orm):
        
        # Deleting model 'Page'
        db.delete_table('coop_page_page')


    models = {
        'coop_page.page': {
            'Meta': {'object_name': 'Page'},
            'content': ('django.db.models.fields.TextField', [], {'default': "u'Page content'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '100', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'default': "u'Page title'"})
        }
    }

    complete_apps = ['coop_page']
