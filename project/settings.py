"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 1.11.29.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wb1!)(-8z)1gmim+w0pk8ag&dwgkt1)j&_4e3ohm=b%s)8hib_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #drf
    'rest_framework',
    'rest_framework.authtoken',
    'django_rest_passwordreset',
    'drf_yasg',
    'corsheaders',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.microsoft',
    'allauth.socialaccount.providers.apple',

    #apps
    'accounts',
    'payment',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',

        # Add the account middleware:
    "allauth.account.middleware.AccountMiddleware",

]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        'DIRS': [BASE_DIR, 'templates/',],
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

WSGI_APPLICATION = 'project.wsgi.application'

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
}

# # Enforce HTTPS
# SECURE_SSL_REDIRECT = True

# # Set HSTS (HTTP Strict Transport Security) to ensure future requests are HTTPS
# SECURE_HSTS_SECONDS = 31536000  # One year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# # Ensure browsers only set cookies over HTTPS
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True



# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True 
CORS_ORIGIN_WHITELIST = (
    # 'http://localhost:3000',
    # 'http://127.0.0.1:5173',
    'https://lawtabby.netlify.app',
)

# CORS_ALLOW_METHODS = [
#     "GET",
#     "POST",
#     "PUT",
#     "PATCH",
#     "DELETE",
#     "OPTIONS",
# ]

# CORS_ALLOW_HEADERS = [
#     "Content-Type",
#     "Authorization",
#     # ...
# ]
# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

# REST_FRAMEWORK = {
#     # Use Django's standard `django.contrib.auth` permissions,
#     # or allow read-only access for unauthenticated users.
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
#     ]
# }

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=100000)
}


ACCOUNT_USERNAME_REQUIRED = False
REST_USE_JWT = True  # or your preferred authentication method
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True



AUTH_USER_MODEL = 'accounts.User'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# GOOGLE_REDIRECT_URL = 'http://127.0.0.1:8000'

GOOGLE_REDIRECT_URL = 'http://127.0.0.1:5173'
# GOOGLE_REDIRECT_URL = 'http://localhost:3000'
MICROSOFT_REDIRECT_URL = 'http://127.0.0.1:5173'
APPlE_REDIRECT_URL = 'http://localhost:3000'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/




MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Email configuration
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'iamtahir727@gmail.com' # Replace with your email address
# EMAIL_HOST_PASSWORD = 'jvyaysudqpyowece'# Replace with your email password
EMAIL_HOST_USER = 'raorehmat11@gmail.com' # Replace with your email address
EMAIL_HOST_PASSWORD='wpmgynkchvbkgcii'

#stripe payment
STRIPE_SECRET_KEY = 'sk_test_51JeDolGB4JYTbuORxnM5WwmuRGHf9KN7LSGnNAkd0D3sGymHhLeOxjFJa1JYemWs08oKdzFMW3VDybh3GFjUrRGu00h5c89flE'
STRIPE_PUBLISHABLE_KEY = 'pk_test_51JeDolGB4JYTbuOR1quYyXWaa0060OlApbeYRRIhOeNBK8DyqDNggLNv9FS5YD6Q3FOsIGCbxfLAVd5izxiPb5HQ00kMW1xXlm'

# google sign in credentials
# settings.py

# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         'APP': {
#             'client_id': '28123279459-4cvinnj0ujpm46b97f1jecefh75jn876.apps.googleusercontent.com',
#             'secret': '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',
#         }
#     }
# }


# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your-google-client-id'
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your-google-client-secret'