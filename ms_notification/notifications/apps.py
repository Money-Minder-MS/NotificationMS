import py_eureka_client.eureka_client as eureka_client
from django.apps import AppConfig
from django.conf import settings


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        try:
            eureka_client.init(
                eureka_server=settings.EUREKA_SERVER_URL,
                app_name=settings.SERVICE_NAME,
                instance_port=settings.SERVICE_PORT,
                instance_host=settings.SERVICE_HOST,
            )
            print(f"[✓] Enregistré sur Eureka : {settings.SERVICE_NAME}:{settings.SERVICE_PORT}")
        except Exception as e:
            print(f"[⚠] Eureka indisponible, le MS continue sans enregistrement : {e}")