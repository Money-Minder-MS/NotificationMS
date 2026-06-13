import os
import sys

import py_eureka_client.eureka_client as eureka_client
from django.apps import AppConfig
from django.conf import settings


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        # Skip Eureka registration pour les commandes admin (migrate, makemigrations,
        # collectstatic, shell, etc.) et pour le process rabbit_consumer.
        # Seul le process daphne/ASGI doit s'enregistrer auprès d'Eureka.
        if os.environ.get('SKIP_EUREKA_REGISTRATION') == '1':
            return

        argv0 = (sys.argv[0] if sys.argv else '').lower()
        if 'manage.py' in argv0 and len(sys.argv) > 1 and sys.argv[1] != 'runserver':
            return
        if 'rabbit_consumer' in argv0:
            return

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