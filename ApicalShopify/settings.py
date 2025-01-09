"""
Django settings for ApicalShopify project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*puip0ps$*)g%@^^yb3b$(%i%m8((af5)xe$2cuoykl654_%=$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shopify',
    'rest_framework',
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',  # Content Security Policy
    'django_ratelimit.middleware.RatelimitMiddleware',  # Rate Limiting
]

ROOT_URLCONF = 'ApicalShopify.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'shopify', 'templates')],
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

WSGI_APPLICATION = 'ApicalShopify.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Require longer passwords
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "shopify" / "static",
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Shopify Settings
SHOPIFY_SETTINGS = {
    'SHOP_NAME': os.getenv('SHOPIFY_SHOP_NAME', ''),
    'ACCESS_TOKEN': os.getenv('SHOPIFY_ACCESS_TOKEN', ''),
    'API_SECRET': os.getenv('SHOPIFY_API_SECRET', ''),
    'API_VERSION': '2024-01',
}

# Security Settings
if DEBUG:
    # Disable security redirects in development
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    # Production security settings remain enabled
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Session Security
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
CSRF_COOKIE_HTTPONLY = True    # Prevent JavaScript access to CSRF cookie
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Session expires when browser closes

# HSTS Settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")  # Adjust based on your needs
CSP_SCRIPT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")

# Frame Options
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking

# XSS Protection
SECURE_BROWSER_XSS_FILTER = True

# Content Type Options
SECURE_CONTENT_TYPE_NOSNIFF = True

# Rate Limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_DEFAULT_LIMITS = {
    'shopify-api': '100/h',  # 100 requests per hour
    'pdf-generation': '50/h',  # 50 PDF generations per hour
}

# API Security
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

# Shopify Webhook Security
SHOPIFY_WEBHOOK_TOLERANCE = 300  # 5 minutes tolerance for webhook timestamps

# File Upload Security
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644
ALLOWED_UPLOAD_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg']

# URL Configuration
APPEND_SLASH = True  # This will automatically handle trailing slashes

# Payment Settings
PAYMENT_SUCCESS_URL = os.getenv('PAYMENT_SUCCESS_URL', 'http://localhost:8000/api/shopify/payment/success/')
PAYMENT_ERROR_URL = os.getenv('PAYMENT_ERROR_URL', 'http://localhost:8000/api/shopify/payment/error/')

# Add to your settings.py
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
