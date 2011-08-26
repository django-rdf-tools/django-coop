# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Schema'
        db.create_table('d2rq_schema', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('prefix', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('d2rq', ['Schema'])

        # Adding model 'MappedModel'
        db.create_table('d2rq_mappedmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('modelname', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('d2rq', ['MappedModel'])

        # Adding model 'MappedField'
        db.create_table('d2rq_mappedfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['d2rq.MappedModel'])),
            ('fieldname', self.gf('django.db.models.fields.TextField')()),
            ('class_prop', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('d2rq', ['MappedField'])


    def backwards(self, orm):
        
        # Deleting model 'Schema'
        db.delete_table('d2rq_schema')

        # Deleting model 'MappedModel'
        db.delete_table('d2rq_mappedmodel')

        # Deleting model 'MappedField'
        db.delete_table('d2rq_mappedfield')


    models = {
        'd2rq.mappedfield': {
            'Meta': {'object_name': 'MappedField'},
            'class_prop': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'fieldname': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['d2rq.MappedModel']"})
        },
        'd2rq.mappedmodel': {
            'Meta': {'object_name': 'MappedModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modelname': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'd2rq.schema': {
            'Meta': {'object_name': 'Schema'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['d2rq']
