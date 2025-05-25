from django.apps import AppConfig

class PerfectParkingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PerfectParking'

    def ready(self):
        import PerfectParking.signals