# NotificationMS — Notification Service

The **notification microservice** for Money Minder MS. A Django service that
consumes events published by the other services over **RabbitMQ** and turns them
into user notifications.

## Tech stack
Python · Django · RabbitMQ (pika/AMQP)

## How it works
Business services (expenses, objectives, revenue, …) publish events to the
`notification.exchange` exchange. This service binds the `notification.queue`
queue with the configured routing keys and processes each message.

## Configuration (environment variables)
RabbitMQ settings are read from the environment, with local defaults:

| Variable | Default |
| --- | --- |
| `RABBITMQ_HOST` | `localhost` |
| `RABBITMQ_PORT` | `5672` |
| `RABBITMQ_USER` | `guest` |
| `RABBITMQ_PASSWORD` | `guest` |

## Run
```bash
cd ms_notification
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt                    # or: pip install django pika
python manage.py migrate
python manage.py runserver
```

Requires a running RabbitMQ broker.

## Part of Money Minder MS

Part of the **Money Minder MS** platform. Full architecture and the other services:
[API-Gateway README](https://github.com/Money-Minder-MS/API-Gateway).

