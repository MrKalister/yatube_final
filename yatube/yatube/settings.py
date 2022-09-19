import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'the-best-secret-key')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# Запрос к проекту через Client()
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]',
    'testserver',
]
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'posts.apps.PostsConfig',
    'users.apps.UsersConfig',
    'core.apps.CoreConfig',
    'about.apps.AboutConfig',
    'sorl.thumbnail',
    'debug_toolbar',
]
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ip addresses for DebugToolbarMiddleware
INTERNAL_IPS = [
    '127.0.0.1',
]
ROOT_URLCONF = 'yatube.urls'
# Директория для хранения шаблонов
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.year.year',
            ],
        },
    },
]
WSGI_APPLICATION = 'yatube.wsgi.application'
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
# Folder for static files
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
# Директория для хранения медиа
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'Posts:index'
# EMAIL_BACKEND = 'django.core.mail.backends.XXX'.
# Вместо XXX указывается название модуля
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# So that messages are not sent to the mail, but come to the folder 'sent_emails'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'

# Page cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

if DEBUG:
    import logging
    logging.basicConfig()
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{pathname}:{lineno} {levelname} {asctime} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
        },
        'loggers': {
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }
