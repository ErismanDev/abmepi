from django.apps import AppConfig


class AssejusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assejus'
    verbose_name = 'Assessoria Jurídica - ASSEJUS'
    
    def ready(self):
        try:
            import assejus.signals
        except ImportError:
            pass
