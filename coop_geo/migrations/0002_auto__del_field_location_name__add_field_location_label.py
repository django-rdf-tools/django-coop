# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Location.name'
        db.delete_column('coop_geo_location', 'name')

        # Adding field 'Location.label'
        db.add_column('coop_geo_location', 'label', self.gf('django.db.models.fields.CharField')(default=u'Default', max_length=150), keep_default=False)


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'Location.name'
        raise RuntimeError("Cannot reverse this migration. 'Location.name' and its values cannot be restored.")

        # Deleting field 'Location.label'
        db.delete_column('coop_geo_location', 'label')


    models = {
        'coop_geo.location': {
            'Meta': {'object_name': 'Location'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'polygon': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['coop_geo']
