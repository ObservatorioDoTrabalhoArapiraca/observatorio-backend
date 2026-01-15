import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='secret-dev-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core',
    'apps.referenciais',
    'apps.movimentacoes',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "https://observatorio-arapiraca.vercel.app",
    "http://localhost:5173",  # Para desenvolvimento
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",  # Permite todos os subdomínios da Vercel
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# ============ DATABASE (FUNCIONA LOCAL E PRODUÇÃO) ============
DATABASE_URL = os.environ.get('DATABASE_URL', None)

# if DATABASE_URL:
    # PRODUÇÃO (Railway/Render)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
    )
}
    # DATABASES = {
    #     'default': dj_database_url.config(
    #         default=DATABASE_URL,
    #         conn_max_age=600,
    #         conn_health_checks=True,
    #     )
    # }
# else:
#     # DESENVOLVIMENTO (Docker local)
#     DATABASES = {
#         'default': {
#             'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
#             # 'NAME': os.environ.get('DB_NAME', 'postgres'),
#             'USER': os.environ.get('DB_USER', 'postgres'),
#             'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
#             # 'HOST': os.environ.get('DB_HOST', 'postgres'),
#             'PORT': os.environ.get('DB_PORT', '5432'),
#         }
#     }

# ============ CACHE (FUNCIONA COM E SEM REDIS) ============
REDIS_URL = os.environ.get('REDIS_URL', None)
REDIS_HOST = os.environ.get('REDIS_HOST', None)

if REDIS_URL:
    # Produção com Redis URL completa
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
elif REDIS_HOST:
    # Local Docker com Redis
    REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    # Fallback: cache em memória (sem Redis)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# ============ ARQUIVOS ESTÁTICOS ============
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
