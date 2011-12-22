# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'NewLabel'
        db.delete_table('skosxl_newlabel')

        # Adding model 'Label'
        db.create_table('skosxl_label', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100, db_index=True)),
            ('language', self.gf('django.db.models.fields.CharField')(default='fr', max_length=10)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('author_uri', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('concept', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='labels', null=True, to=orm['skosxl.Concept'])),
            ('label_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal('skosxl', ['Label'])

        # Deleting field 'SemRelation.type'
        db.delete_column('skosxl_semrelation', 'type')

        # Adding field 'SemRelation.rel_type'
        db.add_column('skosxl_semrelation', 'rel_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1), keep_default=False)

        # Changing field 'Concept.pref_label'
        db.alter_column('skosxl_concept', 'pref_label', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'LabelledItem.tag'
        db.alter_column('skosxl_labelleditem', 'tag_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skosxl.Label']))


    def backwards(self, orm):
        
        # Adding model 'NewLabel'
        db.create_table('skosxl_newlabel', (
            ('concept', self.gf('django.db.models.fields.related.ForeignKey')(related_name='labels', null=True, to=orm['skosxl.Concept'], blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, unique=True, db_index=True)),
            ('label_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('language', self.gf('django.db.models.fields.CharField')(default='fr', max_length=10)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author_uri', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
        ))
        db.send_create_signal('skosxl', ['NewLabel'])

        # Deleting model 'Label'
        db.delete_table('skosxl_label')

        # Adding field 'SemRelation.type'
        db.add_column('skosxl_semrelation', 'type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1), keep_default=False)

        # Deleting field 'SemRelation.rel_type'
        db.delete_column('skosxl_semrelation', 'rel_type')

        # Changing field 'Concept.pref_label'
        db.alter_column('skosxl_concept', 'pref_label', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'LabelledItem.tag'
        db.alter_column('skosxl_labelleditem', 'tag_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skosxl.NewLabel']))


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
            'pref_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'scheme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skosxl.Scheme']", 'null': 'True', 'blank': 'True'}),
            'sem_relations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['skosxl.Concept']", 'through': "orm['skosxl.SemRelation']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_concept': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'skosxl.label': {
            'Meta': {'object_name': 'Label'},
            'author_uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'concept': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'labels'", 'null': 'True', 'to': "orm['skosxl.Concept']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'fr'", 'max_length': '10'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'skosxl.labelleditem': {
            'Meta': {'object_name': 'LabelledItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'skosxl_labelleditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'skosxl_label_items'", 'to': "orm['skosxl.Label']"})
        },
        'skosxl.scheme': {
            'Meta': {'object_name': 'Scheme'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'pref_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        'skosxl.semrelation': {
            'Meta': {'object_name': 'SemRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin_concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rel_origin'", 'to': "orm['skosxl.Concept']"}),
            'rel_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'target_concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rel_target'", 'to': "orm['skosxl.Concept']"})
        }
    }

    complete_apps = ['skosxl']