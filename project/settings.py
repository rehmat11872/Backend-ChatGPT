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
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Define the temporary path
TEMP_PATH = os.path.join(BASE_DIR, 'temp_files')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')


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
    'pdf',
    'chat',
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
        # 'DIRS': [BASE_DIR, 'templates/',],
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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





CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOW_CREDENTIALS = True 
CORS_ORIGIN_WHITELIST = (
    # 'http://localhost:3000',
    'http://127.0.0.1:5173',
    # 'https://lawtabby.netlify.app',
    'https://ai-lawyer.neuracase.com',
)



CORS_ALLOWED_ORIGINS = [
    "https://ai-lawyer.neuracase.com",
    "https://ai-lawyer.neuracase.com",
]

CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
CORS_ALLOW_HEADERS = ['*']
# CORS_ALLOW_HEADERS = [
#     'Authorization',
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


AUTHENTICATION_BACKENDS = [
    # ...
    'allauth.account.auth_backends.AuthenticationBackend',
    # ...
]



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



GOOGLE_REDIRECT_URL = 'https://ai-lawyer.neuracase.com'
MICROSOFT_REDIRECT_URL = 'https://ai-lawyer.neuracase.com'
APPlE_REDIRECT_URL = 'https://ai-lawyer.neuracase.com'
# APPlE_REDIRECT_URL = 'https://377a-119-63-138-173.ngrok-free.app'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/




MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Email settings
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')



# Stripe settings
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')





SOCIALACCOUNT_PROVIDERS = {
    'apple': {
        "APP": {
            "client_id": config('SOCIAL_APPLE_CLIENT_ID'),
            "secret": config('SOCIAL_APPLE_SECRET'),
            "key": config('SOCIAL_APPLE_KEY'),
            "settings": { 
"certificate_key": """-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgCRDgZhaN/Sspvlb7
ryE8D+YChBC2uH97BvNGOKXpHxagCgYIKoZIzj0DAQehRANCAAQdUnewuWFxDIuw
2Mo07NB7fmGzsY+8Proz3t87y5kJuGgCb9QPTVwusFt7q9QxVHJS0uFOn6UAGKvB
AAhUAupv
-----END PRIVATE KEY-----"""

            }
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    }
}






# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your-google-client-id'
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your-google-client-secret'


# Site ID
SITE_ID = config('SITE_ID', default=1, cast=int)


# Apple Sign In settings
SOCIAL_AUTH_APPLE_KEY_ID = config('SOCIAL_AUTH_APPLE_KEY_ID', default='')
SOCIAL_AUTH_APPLE_TEAM_ID = config('SOCIAL_AUTH_APPLE_TEAM_ID', default='')
CLIENT_ID = config('CLIENT_ID', default='')
SOCIAL_AUTH_APPLE_PRIVATE_KEY = config('SOCIAL_AUTH_APPLE_PRIVATE_KEY', default='')


# PayPal settings
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID', default='')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET', default='')
PAYPAL_WEBHOOK_ID = config('PAYPAL_WEBHOOK_ID', default='')

