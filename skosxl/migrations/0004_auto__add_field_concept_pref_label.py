# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Concept.pref_label'
        db.add_column('skosxl_concept', 'pref_label', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Concept.pref_label'
        db.delete_column('skosxl_concept', 'pref_label')


    models = {
        'skosxl.concept': {
            'Meta': {'object_name': 'Concept'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'changenote': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'definition': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'pref_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'sem_relations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['skosxl.Concept']", 'through': "orm['skosxl.SemRelation']", 'symmetrical': 'False'})
        },
        'skosxl.label': {
            'Meta': {'object_name': 'Label'},
            'concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': "orm['skosxl.Concept']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skosxl.Term']"}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'skosxl.maprelation': {
            'Meta': {'object_name': 'MapRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'origin_concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'map_origin'", 'to': "orm['skosxl.Concept']"}),
            'target_label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'voc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skosxl.Vocabulary']"})
        },
        'skosxl.semrelation': {
            'Meta': {'object_name': 'SemRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin_concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rel_origin'", 'to': "orm['skosxl.Concept']"}),
            'target_concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rel_target'", 'to': "orm['skosxl.Concept']"}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'})
        },
        'skosxl.term': {
            'Meta': {'object_name': 'Term'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'concept': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['skosxl.Concept']", 'through': "orm['skosxl.Label']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'fr'", 'max_length': '10'}),
            'literal': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'occurences': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'skosxl.vocabulary': {
            'Meta': {'object_name': 'Vocabulary'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['skosxl']
