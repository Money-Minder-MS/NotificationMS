import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'ms-notification-secret-key-2026'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'channels',
    'notifications',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ms_notification.urls'
ASGI_APPLICATION = 'ms_notification.asgi.application'

# ── PostgreSQL ──────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'ms_notification_db'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'admin'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# ── Redis (WebSocket layer) ─────────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [{
                'host': os.environ.get('REDIS_HOST', 'localhost'),
                'port': int(os.environ.get('REDIS_PORT', '6379')),
                # Empêche le drop des connexions Redis idle sous Docker :
                # keepalive TCP + ping applicatif périodique (détecte et reconnecte
                # les sockets morts → plus de "Timeout reading from redis").
                'socket_keepalive': True,
                'socket_timeout': None,
                'socket_connect_timeout': 5,
                'health_check_interval': 30,
                'retry_on_timeout': True,
            }],
            'capacity': 1500,
            'expiry': 60,
        },
    },
}

# ── RabbitMQ ────────────────────────────────────────────────
RABBITMQ_HOST     = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT     = int(os.environ.get('RABBITMQ_PORT', '5672'))
RABBITMQ_USER     = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD', 'guest')
RABBITMQ_EXCHANGE = 'notification.exchange'
RABBITMQ_QUEUE    = 'notification.queue'
RABBITMQ_ROUTING_KEYS = [
    'notification.revenue.ajoute',
    'notification.depense.ajoutee',
    'notification.objectif.atteint',
    'notification.reclamation.creee',
    'notification.post.cree',
]

# ── Eureka ──────────────────────────────────────────────────
EUREKA_SERVER_URL  = os.environ.get('EUREKA_SERVER_URL', 'http://localhost:8761/eureka')
SERVICE_NAME       = os.environ.get('SERVICE_NAME', 'ms-notification')
SERVICE_HOST       = os.environ.get('SERVICE_HOST', 'localhost')
SERVICE_PORT       = int(os.environ.get('SERVICE_PORT', '8086'))

# ── CORS ────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'