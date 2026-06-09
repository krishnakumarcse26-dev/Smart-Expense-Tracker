from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        """
        ready() is called once when Django starts up.
        We import signals here to register them.
        """
        import accounts.signals  # noqa — importing triggers @receiver decorators
