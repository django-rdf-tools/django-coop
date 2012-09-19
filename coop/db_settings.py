

class GEOFLARouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'geodjangofla':
            return 'geofla_db'
        else:
            return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'geodjangofla':
            return None
        else:
            return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'geodjangofla' or obj2._meta.app_label == 'geodjangofla':
            return None
        else:
            return True

    def allow_syncdb(self, db, model):
        if db == 'geofla_db':
            return None
        if db == 'default' and model._meta.app_label == 'feincms':
            return False
        else:
            return True


DATABASE_ROUTERS = ['coop.db_settings.GEOFLARouter']
