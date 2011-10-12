# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'RssItem'
        db.create_table('rss_sync_rssitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rss_sync.RssSource'])),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('summary', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('rss_sync', ['RssItem'])

        # Adding field 'RssSource.title'
        db.add_column('rss_sync_rsssource', 'title', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True), keep_default=False)

        # Adding field 'RssSource.last_collect'
        db.add_column('rss_sync_rsssource', 'last_collect', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'RssItem'
        db.delete_table('rss_sync_rssitem')

        # Deleting field 'RssSource.title'
        db.delete_column('rss_sync_rsssource', 'title')

        # Deleting field 'RssSource.last_collect'
        db.delete_column('rss_sync_rsssource', 'last_collect')


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
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['rss_sync']
