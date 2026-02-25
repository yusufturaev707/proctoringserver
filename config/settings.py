import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t", '11')

ALLOWED_HOSTS = ['w1.uzbmb.uz', 'localhost', '127.0.0.1']
# ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ["https://w1.uzbmb.uz", "https://www.w1.uzbmb.uz"]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    # Unfold — django.contrib.admin DAN OLDIN bo'lishi shart
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd-party ilovalar
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    "django_filters",

    # apps
    'apps.regions',
    'apps.users',
    'apps.settings',
    'apps.exams',
    'apps.notification',
    'apps.coco_class',
]

# ─── Django Unfold ──────────────────────────────────────────────────────────
UNFOLD = {
    "SITE_TITLE": "Proktoring",
    "SITE_HEADER": "Proktoring Tizimi",
    "SITE_URL": "/",
    "SITE_SYMBOL": "shield_person",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "SHOW_BACK_BUTTON": True,
    "COLORS": {
        "primary": {
            "50": "238 242 255",
            "100": "224 231 255",
            "200": "199 210 254",
            "300": "165 180 252",
            "400": "129 140 248",
            "500": "99 102 241",
            "600": "79 70 229",
            "700": "67 56 202",
            "800": "55 48 163",
            "900": "49 46 129",
            "950": "30 27 75",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Foydalanuvchilar"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Foydalanuvchilar"),
                        "icon": "group",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                    {
                        "title": _("Rollar"),
                        "icon": "manage_accounts",
                        "link": reverse_lazy("admin:users_role_changelist"),
                    },
                ],
            },
            {
                "title": _("Viloyatlar"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Viloyatlar"),
                        "icon": "map",
                        "link": reverse_lazy("admin:regions_region_changelist"),
                    },
                    {
                        "title": _("Binolar"),
                        "icon": "domain",
                        "link": reverse_lazy("admin:regions_zone_changelist"),
                    },
                ],
            },
            {
                "title": _("Imtihonlar"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Testlar"),
                        "icon": "description",
                        "link": reverse_lazy("admin:exams_test_changelist"),
                    },
                ],
            },
            {
                "title": _("Sozlamalar"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Sozlamalar"),
                        "icon": "tune",
                        "link": reverse_lazy("admin:settings_settings_changelist"),
                    },
                    {
                        "title": _("Public IP"),
                        "icon": "public",
                        "link": reverse_lazy("admin:settings_allowpublicip_changelist"),
                    },
                    {
                        "title": _("Chiqish paroli"),
                        "icon": "lock",
                        "link": reverse_lazy("admin:settings_exitpassword_changelist"),
                    },
                    {
                        "title": _("Kompyuterlar"),
                        "icon": "computer",
                        "link": reverse_lazy("admin:settings_computer_changelist"),
                    },
                    {
                        "title": _("IP Kameralar"),
                        "icon": "videocam",
                        "link": reverse_lazy("admin:settings_ipcamera_changelist"),
                    },
                ],
            },
            {
                "title": _("Xabarlar"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Ogohlantirishlar"),
                        "icon": "notifications_active",
                        "link": reverse_lazy("admin:notification_warningnotification_changelist"),
                    },
                    {
                        "title": _("O'rnatish loglari"),
                        "icon": "install_desktop",
                        "link": reverse_lazy("admin:notification_installinfolog_changelist"),
                    },
                ],
            },
            {
                "title": _("AI Model Sinflar"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Model versiyalari"),
                        "icon": "model_training",
                        "link": reverse_lazy("admin:coco_class_modelversion_changelist"),
                    },
                    {
                        "title": _("Ob'ekt guruhlari"),
                        "icon": "category",
                        "link": reverse_lazy("admin:coco_class_cocoobjectgroup_changelist"),
                    },
                    {
                        "title": _("Ob'ektlar"),
                        "icon": "visibility",
                        "link": reverse_lazy("admin:coco_class_cocoobject_changelist"),
                    },
                ],
            },
            {
                "title": _("RDP va Keyboard"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("RDP ob'ektlari"),
                        "icon": "desktop_windows",
                        "link": reverse_lazy("admin:coco_class_rdpobject_changelist"),
                    },
                    {
                        "title": _("Hot Keys"),
                        "icon": "keyboard",
                        "link": reverse_lazy("admin:coco_class_hotkeyboardkey_changelist"),
                    },
                ],
            },
        ],
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
ASGI_APPLICATION = "config.asgi.application"
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760
DJANGO_ALLOW_ASYNC_UNSAFE = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        'rest_framework.throttling.UserRateThrottle',
        'core.throttles.IPRateThrottle',
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "200/min",
        'ip': '1000/hour',
        'user': '1000/hour',
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("POSTGRES_DB"),
        'USER': os.getenv("POSTGRES_USER"),
        'PASSWORD': os.getenv("POSTGRES_PASSWORD"),
        'HOST': os.getenv("POSTGRES_HOST"),
        'PORT': os.getenv("POSTGRES_PORT"),
    }
}

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AUTH_USER_MODEL = 'users.User'

# Celery settings
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tashkent'

if os.name == 'nt':  # Windows
    CELERY_WORKER_POOL = 'solo'
    CELERY_WORKER_CONCURRENCY = 1
else:  # Linux/Mac
    CELERY_WORKER_POOL = 'prefork'
    CELERY_WORKER_CONCURRENCY = 4

# External api settings
EXTERNAL_API_SETTINGS = {
    'BASE_URL': os.getenv('BASE_API_URL', ''),
    'API_KEY': os.getenv('BASE_API_KEY', ''),
    'TIMEOUT': int(os.getenv('BASE_TIMEOUT', 30)),
}
