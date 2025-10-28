from django.apps import AppConfig
from django.db.models.signals import post_migrate

class MarketingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marketing'
    verbose_name = 'Marketing'

    def ready(self):
        from .signals import asignar_permisos_marketing
        
        
        post_migrate.connect(asignar_permisos_marketing, sender=self)