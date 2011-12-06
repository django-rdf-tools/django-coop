# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'SimilarConcept'
        db.delete_table('skosxl_similarconcept')

        # Adding model 'MapRelation'
        db.create_table('skosxl_maprelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('origin_concept', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skosxl.Concept'])),
            ('target_label', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('voc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skosxl.Vocabulary'])),
            ('match_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal('skosxl', ['MapRelation'])

        # Changing field 'Term.occurences'
        db.alter_column('skosxl_term', 'occurences', self.gf('django.db.models.fields.IntegerField')())


    def backwards(self, orm):
        
        # Adding model 'SimilarConcept'
        db.create_table('skosxl_similarconcept', (
            ('match_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('voc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skosxl.Vocabulary'])),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('Preflabel', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('similar_to', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skosxl.Concept'])),
        ))
        db.send_create_signal('skosxl', ['SimilarConcept'])

        # Deleting model 'MapRelation'
        db.delete_table('skosxl_maprelation')

        # Changing field 'Term.occurences'
        db.alter_column('skosxl_term', 'occurences', self.gf('django.db.models.fields.IntegerField')(null=True))


    models = {
        'skosxl.concept': {
            'Meta': {'object_name': 'Concept'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'changenote': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'definition': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
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
            'origin_concept': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skosxl.Concept']"}),
            'target_label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'voc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skosxl.Vocabulary']"})
        },
        'skosxl.semrelation': {
            'Meta': {'object_name': 'SemRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin_concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'origin'", 'to': "orm['skosxl.Concept']"}),
            'target_concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'target'", 'to': "orm['skosxl.Concept']"}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'})
        },
        'skosxl.term': {
            'Meta': {'object_name': 'Term'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'concept': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['skosxl.Concept']", 'through': "orm['skosxl.Label']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'@fr'", 'max_length': '10'}),
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
