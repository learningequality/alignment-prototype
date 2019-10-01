class DbRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read remote models go to remote database.
        """
        if model._meta.app_label == 'commonstandardsproject':
            return 'standards'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write remote models go to the remote database.
        """
        if model._meta.app_label == 'commonstandardsproject':
            return 'standards'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Do not allow relations involving the remote database
        """
        if obj1._meta.app_label == 'commonstandardsproject' or \
           obj2._meta.app_label == 'commonstandardsproject':
           return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Do not allow migrations on the remote database
        """
        if model._meta.app_label == 'commonstandardsproject':
            return False
        return True