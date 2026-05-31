import sys
import os

# Remonter 2 niveaux pour trouver le module ms_notification
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ms_notification.settings')

import django
django.setup()

import json
import pika
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from notifications.models import Notification


def handle_message(ch, method, properties, body):
    """Appelé à chaque message RabbitMQ reçu."""
    try:
        payload = json.loads(body)

        user_id    = payload.get('userId')
        message    = payload.get('message', '')
        notif_type = payload.get('type', '')
        data       = payload.get('data', {})

        # 1. Sauvegarder en base PostgreSQL
        notif = Notification.objects.create(
            user_id=user_id,
            message=message,
            type=notif_type,
            data=data,
            is_read=False,
        )

        # 2. Envoyer en temps réel via WebSocket au bon utilisateur
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                'type': 'send_notification',
                'notification': {
                    'id':        notif.id,
                    'message':   notif.message,
                    'type':      notif.type,
                    'data':      notif.data,
                    'is_read':   notif.is_read,
                    'timestamp': notif.timestamp.isoformat(),
                }
            }
        )

        print(f"[✓] Notification créée et envoyée → user {user_id} : {message}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    except Exception as e:
        print(f"[✗] Erreur traitement message : {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)


def start_consumer():
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER,
        settings.RABBITMQ_PASSWORD
    )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=credentials,
        )
    )
    channel = connection.channel()

    # Déclarer l'exchange
    channel.exchange_declare(
        exchange=settings.RABBITMQ_EXCHANGE,
        exchange_type='topic',
        durable=True
    )

    # Déclarer la queue
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)

    # Binder toutes les routing keys à la queue
    for routing_key in settings.RABBITMQ_ROUTING_KEYS:
        channel.queue_bind(
            exchange=settings.RABBITMQ_EXCHANGE,
            queue=settings.RABBITMQ_QUEUE,
            routing_key=routing_key
        )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=settings.RABBITMQ_QUEUE,
        on_message_callback=handle_message
    )

    print("[*] MS Notification en écoute sur RabbitMQ...")
    channel.start_consuming()


if __name__ == '__main__':
    start_consumer()