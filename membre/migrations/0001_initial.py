# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SameAs'
        db.create_table('membre_sameas', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uri', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
        ))
        db.send_create_signal('membre', ['SameAs'])


    def backwards(self, orm):
        
        # Deleting model 'SameAs'
        db.delete_table('membre_sameas')


    models = {
        'membre.sameas': {
            'Meta': {'object_name': 'SameAs'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uri': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        }
    }

    complete_apps = ['membre']
