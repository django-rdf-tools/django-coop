# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'RssSource', fields ['url']
        db.create_unique('rss_sync_rsssource', ['url'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'RssSource', fields ['url']
        db.delete_unique('rss_sync_rsssource', ['url'])


    models = {
        'rss_sync.rssitem': {
            'Meta': {'object_name': 'RssItem'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rss_sync.RssSource']"}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'rss_sync.rsssource': {
            'Meta': {'object_name': 'RssSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_collect': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        }
    }

    complete_apps = ['rss_sync']
