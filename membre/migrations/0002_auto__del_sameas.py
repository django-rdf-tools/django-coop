# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'SameAs'
        db.delete_table('membre_sameas')


    def backwards(self, orm):
        
        # Adding model 'SameAs'
        db.create_table('membre_sameas', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uri', self.gf('django.db.models.fields.URLField')(max_length=200, unique=True)),
        ))
        db.send_create_signal('membre', ['SameAs'])


    models = {
        
    }

    complete_apps = ['membre']
