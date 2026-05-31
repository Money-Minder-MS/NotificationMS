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
        'NAME': 'ms_notification_db',
        'USER': 'postgres',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# ── Redis (WebSocket layer) ─────────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('localhost', 6379)],
        },
    },
}

# ── RabbitMQ ────────────────────────────────────────────────
RABBITMQ_HOST     = 'localhost'
RABBITMQ_PORT     = 5672
RABBITMQ_USER     = 'guest'
RABBITMQ_PASSWORD = 'guest'
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
EUREKA_SERVER_URL  = 'http://localhost:8761/eureka'
SERVICE_NAME       = 'ms-notification'
SERVICE_HOST       = 'localhost'
SERVICE_PORT       = 8086

# ── CORS ────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'