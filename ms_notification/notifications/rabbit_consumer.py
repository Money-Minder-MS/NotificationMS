import sys
import os

# rabbit_consumer.py est à /app/notifications/, le package ms_notification est à /app/
# → remonter 1 seul niveau pour le trouver
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[✗] Erreur traitement message : {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def _open_rabbit_connection():
    """Ouvre la connexion RabbitMQ avec retry exponentiel.

    RabbitMQ peut accepter le TCP sans être prêt à AMQP : on retente jusqu'à
    ~2 minutes avant d'abandonner.
    """
    import time as _time

    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER,
        settings.RABBITMQ_PASSWORD
    )
    params = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=30,
        blocked_connection_timeout=30,
        connection_attempts=1,
        socket_timeout=5,
    )
    delay = 2
    for attempt in range(1, 16):
        try:
            return pika.BlockingConnection(params)
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[…] RabbitMQ pas encore prêt (tentative {attempt}/15) : {e}")
            _time.sleep(delay)
            delay = min(delay + 2, 15)
    raise RuntimeError("RabbitMQ injoignable après 15 tentatives")


def start_consumer():
    connection = _open_rabbit_connection()
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