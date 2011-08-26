# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SchemaClass'
        db.create_table('d2rq_schemaclass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['d2rq.Schema'])),
            ('class_label', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('class_name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('d2rq', ['SchemaClass'])

        # Adding model 'SchemaProperty'
        db.create_table('d2rq_schemaproperty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['d2rq.Schema'])),
            ('prop_label', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('prop_name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('d2rq', ['SchemaProperty'])

        # Deleting field 'MappedField.class_prop'
        db.delete_column('d2rq_mappedfield', 'class_prop')

        # Deleting field 'MappedField.fieldname'
        db.delete_column('d2rq_mappedfield', 'fieldname')

        # Adding field 'MappedField.field_name'
        db.add_column('d2rq_mappedfield', 'field_name', self.gf('django.db.models.fields.TextField')(null=True), keep_default=False)

        # Adding field 'MappedField.rdf_proprety'
        db.add_column('d2rq_mappedfield', 'rdf_proprety', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['d2rq.SchemaProperty'], null=True), keep_default=False)

        # Deleting field 'MappedModel.modelname'
        db.delete_column('d2rq_mappedmodel', 'modelname')

        # Adding field 'MappedModel.model_name'
        db.add_column('d2rq_mappedmodel', 'model_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True), keep_default=False)

        # Adding field 'MappedModel.rdf_class'
        db.add_column('d2rq_mappedmodel', 'rdf_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['d2rq.SchemaClass'], null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'SchemaClass'
        db.delete_table('d2rq_schemaclass')

        # Deleting model 'SchemaProperty'
        db.delete_table('d2rq_schemaproperty')

        # Adding field 'MappedField.class_prop'
        db.add_column('d2rq_mappedfield', 'class_prop', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # User chose to not deal with backwards NULL issues for 'MappedField.fieldname'
        raise RuntimeError("Cannot reverse this migration. 'MappedField.fieldname' and its values cannot be restored.")

        # Deleting field 'MappedField.field_name'
        db.delete_column('d2rq_mappedfield', 'field_name')

        # Deleting field 'MappedField.rdf_proprety'
        db.delete_column('d2rq_mappedfield', 'rdf_proprety_id')

        # User chose to not deal with backwards NULL issues for 'MappedModel.modelname'
        raise RuntimeError("Cannot reverse this migration. 'MappedModel.modelname' and its values cannot be restored.")

        # Deleting field 'MappedModel.model_name'
        db.delete_column('d2rq_mappedmodel', 'model_name')

        # Deleting field 'MappedModel.rdf_class'
        db.delete_column('d2rq_mappedmodel', 'rdf_class_id')


    models = {
        'd2rq.mappedfield': {
            'Meta': {'object_name': 'MappedField'},
            'field_name': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['d2rq.MappedModel']"}),
            'rdf_proprety': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['d2rq.SchemaProperty']", 'null': 'True'})
        },
        'd2rq.mappedmodel': {
            'Meta': {'object_name': 'MappedModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'rdf_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['d2rq.SchemaClass']", 'null': 'True'})
        },
        'd2rq.schema': {
            'Meta': {'object_name': 'Schema'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'd2rq.schemaclass': {
            'Meta': {'object_name': 'SchemaClass'},
            'class_label': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['d2rq.Schema']"})
        },
        'd2rq.schemaproperty': {
            'Meta': {'object_name': 'SchemaProperty'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prop_label': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'prop_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['d2rq.Schema']"})
        }
    }

    complete_apps = ['d2rq']
