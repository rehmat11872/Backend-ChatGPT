import os
import datetime
from decouple import config
import dj_database_url
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent


# ===========================================
# GENERAL SETTINGS
# ===========================================


ENV = config("ENV", default="development")
DEBUG = config("DEBUG", default=False, cast=bool)
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())



# ===========================================
# APPLICATIONS
# ===========================================
# --- Django Core Apps ---
DJANGO_APPS = [
    "jazzmin", 
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

# --- Third-Party Apps ---
THIRD_PARTY_APPS = [
    "drf_spectacular",
    "rest_framework",
    "rest_framework.authtoken",
    "django_rest_passwordreset",
    "drf_yasg",
    "corsheaders",
    "dj_rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.microsoft",
    "allauth.socialaccount.providers.apple",     
]

# --- Local Apps ---
LOCAL_APPS = [
    "accounts",
    "payment",
    "pdf",
    "legal_ai_agent",
    "document_summarizer",
]

# --- Combine All Apps ---
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS



# ===========================================
# Jazzmin Settings - Optimized Configuration
# ===========================================

JAZZMIN_SETTINGS = {
    # Title & Branding
    "site_title": "Legal AI Admin",
    "site_header": "Legal AI Administration",
    "site_brand": "Legal AI",
    "welcome_sign": "Welcome to Legal AI Admin",
    "copyright": "Legal AI Admin",
    
    # Search
    "search_model": ["accounts.User", "auth.Group"],
    
    # Top Menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.User"},
        {"app": "accounts"},
    ],

    # User Menu
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],

    # Side Menu
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    # Icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "accounts.User": "fas fa-user-circle",
        "accounts.Subscription": "fas fa-credit-card",
        "payment": "fas fa-money-bill",
        "pdf": "fas fa-file-pdf",
        "legal_ai_agent": "fas fa-robot",
    },
    
    # Default Icons
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # Related Modal
    "related_modal_active": False,
    
    # Custom CSS/JS
    "custom_css": "admin/css/custom.css",
    "custom_js": None,
    
    # Show UI Builder
    "show_ui_builder": False,
    
    # Changeform Format
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    
    # Language Chooser
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": False
}


# ===========================================
# MIDDLEWARE
# ===========================================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "project.urls"

# ===========================================
# TEMPLATES
# ===========================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


# ===========================================
# DATABASE
# ===========================================
DATABASE_URL = config("DATABASE_URL", default=None)

if DATABASE_URL:
    # If DATABASE_URL exists, assume PostgreSQL (or other DB from the URL)
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=False)
    }
else:
    # Fallback to SQLite automatically
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }



# ===========================================
# PASSWORD VALIDATORS
# ===========================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]



# ===========================================
# INTERNATIONALIZATION
# ===========================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ===========================================
# STATIC & MEDIA FILES
# ===========================================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Make Django respect the proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# ===========================================
# EMAIL SETTINGS
# ===========================================
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")


# ===========================================
# CORS SETTINGS
# ===========================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="", cast=Csv())
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://ai-lawyer.neuracase.com",
    "https://lawtabby-frontend.netlify.app",
]

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ["*"]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    # 'http://localhost:3000',
    'http://127.0.0.1:5173',
    'http://localhost:5173',
    # 'https://lawtabby.netlify.app',
    'https://ai-lawyer.neuracase.com',
    'https://lawtabby-new-design.netlify.app',
    "https://lawtabby-frontend.netlify.app",
)


# ===========================================
# REST FRAMEWORK
# ===========================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",  
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}



# ===========================================
# SPECTACULAR (API DOCS)
# ===========================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'Legal AI Chat',
    'DESCRIPTION': 'AI-powered legal chat assistant (Lexi) with document upload and streaming GPT responses.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATION_PARAMETERS': True,
    'TAGS': [
        {'name': 'Legal AI Chat', 'description': 'Interact with Lexi — a U.S. legal assistant.'},
    ],
    'SERVE_PUBLIC': True,
    'SECURITY': [
        {'Bearer': []},
    ],
}


# ===========================================
# AUTHENTICATION
# ===========================================
AUTHENTICATION_BACKENDS = ["allauth.account.auth_backends.AuthenticationBackend"]
AUTH_USER_MODEL = "accounts.User"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
REST_USE_JWT = True

JWT_AUTH = {
    "JWT_AUTH_HEADER_PREFIX": "JWT",
    "JWT_EXPIRATION_DELTA": datetime.timedelta(hours=24),
}


# ===========================================
# THIRD PARTY KEYS
# ===========================================
# stripe setting
STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")
# Apple Sign In settings
SOCIAL_AUTH_APPLE_KEY_ID = config('SOCIAL_AUTH_APPLE_KEY_ID', default='')
SOCIAL_AUTH_APPLE_TEAM_ID = config('SOCIAL_AUTH_APPLE_TEAM_ID', default='')
CLIENT_ID = config('CLIENT_ID', default='')
SOCIAL_AUTH_APPLE_PRIVATE_KEY = config('SOCIAL_AUTH_APPLE_PRIVATE_KEY', default='')
# PayPal settings
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID', default='')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET', default='')
PAYPAL_WEBHOOK_ID = config('PAYPAL_WEBHOOK_ID', default='')
# Open API settings
OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
# Courtlisterner API settings
COURTLISTENER_API_KEY = config("COURTLISTENER_API_KEY", default="")


GOOGLE_REDIRECT_URL = 'https://ai-lawyer.neuracase.com'
MICROSOFT_REDIRECT_URL = 'https://ai-lawyer.neuracase.com'
APPlE_REDIRECT_URL = 'https://ai-lawyer.neuracase.com'



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


# ===========================================
# SITE
# ===========================================
SITE_ID = config("SITE_ID", default=1, cast=int)



# ===========================================
# Define the temporary path
# ===========================================
TEMP_PATH = os.path.join(BASE_DIR, 'temp_files')

# ===========================================
# ENV-BASED OVERRIDES
# ===========================================
if ENV == "production":
    DEBUG = False
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
else:
    DEBUG = True

# # Completely disable CSRF for testing
# CSRF_COOKIE_SECURE = False
# CSRF_USE_SESSIONS = False
# CSRF_COOKIE_HTTPONLY = False



























