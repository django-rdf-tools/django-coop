# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Engagement'
        db.create_table('coop_local_engagement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('membre', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coop_local.Membre'])),
            ('initiative', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coop_local.Initiative'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coop_local.Role'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
        ))
        db.send_create_signal('coop_local', ['Engagement'])

        # Adding model 'Membre'
        db.create_table('coop_local_membre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, null=True, blank=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('prenom', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('adresse', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ville', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('code_postal', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
            ('telephone_fixe', self.gf('django.db.models.fields.CharField')(max_length=14, blank=True)),
            ('telephone_portable', self.gf('django.db.models.fields.CharField')(max_length=14, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('adherent', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('coop_local', ['Membre'])

        # Adding model 'Role'
        db.create_table('coop_local_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
        ))
        db.send_create_signal('coop_local', ['Role'])

        # Adding model 'Calendar'
        db.create_table('coop_local_calendar', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
        ))
        db.send_create_signal('coop_local', ['Calendar'])

        # Adding model 'Event'
        db.create_table('coop_local_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('calendar', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coop_local.Event'])),
            ('org', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coop_local.Initiative'], null=True, blank=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coop_local.Membre'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('datetime', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2011, 9, 5, 21, 51, 34, 379037))),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
        ))
        db.send_create_signal('coop_local', ['Event'])

        # Adding model 'Exchange'
        db.create_table('coop_local_exchange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('org', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coop_local.Initiative'], null=True, blank=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coop_local.Membre'])),
            ('etype', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('expiration', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2011, 9, 5, 21, 51, 34, 390074), null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
        ))
        db.send_create_signal('coop_local', ['Exchange'])

        # Adding model 'Transaction'
        db.create_table('coop_local_transaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='origin', to=orm['coop_local.Exchange'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(related_name='destination', to=orm['coop_local.Exchange'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
        ))
        db.send_create_signal('coop_local', ['Transaction'])

        # Adding model 'Site'
        db.create_table('coop_local_site', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coop_local.Initiative'], null=True, blank=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coop_local.Event'], null=True, blank=True)),
            ('exchange', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coop_local.Exchange'], null=True, blank=True)),
            ('site_principal', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('adr1', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('adr2', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('latlong', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
        ))
        db.send_create_signal('coop_local', ['Site'])

        # Adding model 'Initiative'
        db.create_table('coop_local_initiative', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('telephone_fixe', self.gf('django.db.models.fields.CharField')(max_length=14, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('web', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('rss', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('secteur_fse', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal('coop_local', ['Initiative'])


    def backwards(self, orm):
        
        # Deleting model 'Engagement'
        db.delete_table('coop_local_engagement')

        # Deleting model 'Membre'
        db.delete_table('coop_local_membre')

        # Deleting model 'Role'
        db.delete_table('coop_local_role')

        # Deleting model 'Calendar'
        db.delete_table('coop_local_calendar')

        # Deleting model 'Event'
        db.delete_table('coop_local_event')

        # Deleting model 'Exchange'
        db.delete_table('coop_local_exchange')

        # Deleting model 'Transaction'
        db.delete_table('coop_local_transaction')

        # Deleting model 'Site'
        db.delete_table('coop_local_site')

        # Deleting model 'Initiative'
        db.delete_table('coop_local_initiative')


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
        'coop_local.calendar': {
            'Meta': {'object_name': 'Calendar'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        'coop_local.engagement': {
            'Meta': {'object_name': 'Engagement'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiative': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_local.Initiative']"}),
            'membre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_local.Membre']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_local.Role']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        },
        'coop_local.event': {
            'Meta': {'object_name': 'Event'},
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_local.Event']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'datetime': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2011, 9, 5, 21, 51, 34, 406883)'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_local.Membre']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'org': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_local.Initiative']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        },
        'coop_local.exchange': {
            'Meta': {'object_name': 'Exchange'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'etype': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'expiration': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2011, 9, 5, 21, 51, 34, 418287)', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_local.Membre']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'org': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_local.Initiative']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        'coop_local.initiative': {
            'Meta': {'object_name': 'Initiative'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'rss': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'secteur_fse': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'telephone_fixe': ('django.db.models.fields.CharField', [], {'max_length': '14', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'web': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'coop_local.membre': {
            'Meta': {'object_name': 'Membre'},
            'adherent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'adresse': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'code_postal': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'telephone_fixe': ('django.db.models.fields.CharField', [], {'max_length': '14', 'blank': 'True'}),
            'telephone_portable': ('django.db.models.fields.CharField', [], {'max_length': '14', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'ville': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'coop_local.role': {
            'Meta': {'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'coop_local.site': {
            'Meta': {'object_name': 'Site'},
            'adr1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'adr2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_local.Event']", 'null': 'True', 'blank': 'True'}),
            'exchange': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_local.Exchange']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latlong': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_local.Initiative']", 'null': 'True', 'blank': 'True'}),
            'site_principal': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        'coop_local.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'destination'", 'to': "orm['coop_local.Exchange']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'origin'", 'to': "orm['coop_local.Exchange']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        }
    }

    complete_apps = ['coop_local']
