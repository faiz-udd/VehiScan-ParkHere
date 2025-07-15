from django.apps import AppConfig

class VehiscanWebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vehiscanWebsite'

    def ready(self):
        import vehiscanWebsite.signals

