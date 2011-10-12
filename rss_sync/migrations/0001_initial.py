# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'RssSource'
        db.create_table('rss_sync_rsssource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('rss_sync', ['RssSource'])


    def backwards(self, orm):
        
        # Deleting model 'RssSource'
        db.delete_table('rss_sync_rsssource')


    models = {
        'rss_sync.rsssource': {
            'Meta': {'object_name': 'RssSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['rss_sync']
