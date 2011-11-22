# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Concept'
        db.create_table('skosxl_concept', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('definition', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('changenote', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
        ))
        db.send_create_signal('skosxl', ['Concept'])

        # Adding model 'Term'
        db.create_table('skosxl_term', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('literal', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(default='@fr', max_length=10)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
        ))
        db.send_create_signal('skosxl', ['Term'])

        # Adding model 'Vocabulary'
        db.create_table('skosxl_vocabulary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('info_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('skosxl', ['Vocabulary'])

        # Adding model 'Label'
        db.create_table('skosxl_label', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skosxl.Term'])),
            ('concept', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skosxl.Concept'])),
            ('type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal('skosxl', ['Label'])

        # Adding model 'SemRelation'
        db.create_table('skosxl_semrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('origin_concept', self.gf('django.db.models.fields.related.ForeignKey')(related_name='origin', to=orm['skosxl.Concept'])),
            ('target_concept', self.gf('django.db.models.fields.related.ForeignKey')(related_name='target', to=orm['skosxl.Concept'])),
            ('type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=2)),
        ))
        db.send_create_signal('skosxl', ['SemRelation'])

        # Adding model 'SimilarConcept'
        db.create_table('skosxl_similarconcept', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('similar_to', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skosxl.Concept'])),
            ('Preflabel', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('voc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skosxl.Vocabulary'])),
            ('match_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal('skosxl', ['SimilarConcept'])


    def backwards(self, orm):
        
        # Deleting model 'Concept'
        db.delete_table('skosxl_concept')

        # Deleting model 'Term'
        db.delete_table('skosxl_term')

        # Deleting model 'Vocabulary'
        db.delete_table('skosxl_vocabulary')

        # Deleting model 'Label'
        db.delete_table('skosxl_label')

        # Deleting model 'SemRelation'
        db.delete_table('skosxl_semrelation')

        # Deleting model 'SimilarConcept'
        db.delete_table('skosxl_similarconcept')


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
            'concept': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skosxl.Concept']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skosxl.Term']"}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'skosxl.semrelation': {
            'Meta': {'object_name': 'SemRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin_concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'origin'", 'to': "orm['skosxl.Concept']"}),
            'target_concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'target'", 'to': "orm['skosxl.Concept']"}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '2'})
        },
        'skosxl.similarconcept': {
            'Meta': {'object_name': 'SimilarConcept'},
            'Preflabel': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'similar_to': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skosxl.Concept']"}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'voc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skosxl.Vocabulary']"})
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
