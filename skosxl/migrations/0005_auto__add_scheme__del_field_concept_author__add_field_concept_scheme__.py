# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Scheme'
        db.create_table('skosxl_scheme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pref_label', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
        ))
        db.send_create_signal('skosxl', ['Scheme'])

        # Deleting field 'Concept.author'
        db.delete_column('skosxl_concept', 'author')

        # Adding field 'Concept.scheme'
        db.add_column('skosxl_concept', 'scheme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skosxl.Scheme'], null=True, blank=True), keep_default=False)

        # Adding field 'Concept.status'
        db.add_column('skosxl_concept', 'status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0), keep_default=False)

        # Adding field 'Concept.user'
        db.add_column('skosxl_concept', 'user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True), keep_default=False)

        # Adding field 'Concept.uri'
        db.add_column('skosxl_concept', 'uri', self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True), keep_default=False)

        # Adding field 'Concept.author_uri'
        db.add_column('skosxl_concept', 'author_uri', self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True), keep_default=False)

        # Adding field 'Concept.top_concept'
        db.add_column('skosxl_concept', 'top_concept', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Deleting field 'Term.author'
        db.delete_column('skosxl_term', 'author')

        # Adding field 'Term.user'
        db.add_column('skosxl_term', 'user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True), keep_default=False)

        # Adding field 'Term.uri'
        db.add_column('skosxl_term', 'uri', self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True), keep_default=False)

        # Adding field 'Term.author_uri'
        db.add_column('skosxl_term', 'author_uri', self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'Scheme'
        db.delete_table('skosxl_scheme')

        # Adding field 'Concept.author'
        db.add_column('skosxl_concept', 'author', self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True), keep_default=False)

        # Deleting field 'Concept.scheme'
        db.delete_column('skosxl_concept', 'scheme_id')

        # Deleting field 'Concept.status'
        db.delete_column('skosxl_concept', 'status')

        # Deleting field 'Concept.user'
        db.delete_column('skosxl_concept', 'user_id')

        # Deleting field 'Concept.uri'
        db.delete_column('skosxl_concept', 'uri')

        # Deleting field 'Concept.author_uri'
        db.delete_column('skosxl_concept', 'author_uri')

        # Deleting field 'Concept.top_concept'
        db.delete_column('skosxl_concept', 'top_concept')

        # Adding field 'Term.author'
        db.add_column('skosxl_term', 'author', self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True), keep_default=False)

        # Deleting field 'Term.user'
        db.delete_column('skosxl_term', 'user_id')

        # Deleting field 'Term.uri'
        db.delete_column('skosxl_term', 'uri')

        # Deleting field 'Term.author_uri'
        db.delete_column('skosxl_term', 'author_uri')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'skosxl.concept': {
            'Meta': {'object_name': 'Concept'},
            'author_uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'changenote': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'definition': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'pref_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'scheme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skosxl.Scheme']", 'null': 'True', 'blank': 'True'}),
            'sem_relations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['skosxl.Concept']", 'through': "orm['skosxl.SemRelation']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_concept': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
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
        'skosxl.scheme': {
            'Meta': {'object_name': 'Scheme'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'pref_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
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
            'author_uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'concept': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['skosxl.Concept']", 'through': "orm['skosxl.Label']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'fr'", 'max_length': '10'}),
            'literal': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'occurences': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'skosxl.vocabulary': {
            'Meta': {'object_name': 'Vocabulary'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['skosxl']
