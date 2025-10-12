"""
Django settings for vendoro project.
"""

from pathlib import Path
import os

from django.contrib.messages import constants as messages
import cloudinary
import dj_database_url

# Paths and local env loader
BASE_DIR = Path(__file__).resolve().parent.parent

if os.path.isfile(BASE_DIR / "env.py"):
    import env  # noqa; sets os.environ values


# Env helpers
def env_csv(key: str, default: str = "") -> list[str]:
    return [
        x.strip() for x in os.environ.get(key, default).split(",")
        if x.strip()
    ]


def env_bool(key: str, default: str = "0") -> bool:
    return (
        os.environ.get(key, default).strip()
        in {"1", "true", "True", "yes", "YES"}
    )


def env_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, str(default)))
    except Exception:
        return default


# Core settings
SECRET_KEY = os.environ.get("SECRET_KEY", default='your secret key')
DEBUG = os.environ.get("DEBUG", "1") == "1"

ALLOWED_HOSTS = env_csv(
    "ALLOWED_HOSTS",
    "imn-vendoro-55af0b986025.herokuapp.com,localhost,127.0.0.1"
)

# Heroku proxy/HTTPS

# In dev: no HTTPS enforcement
if DEBUG:
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
    # Make form posts from local origins work smoothly
    CSRF_TRUSTED_ORIGINS = env_csv(
        "CSRF_TRUSTED_ORIGINS",
        "http://localhost,http://localhost:8000",
    )
else:
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "1") == "1"
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
    CSRF_TRUSTED_ORIGINS = env_csv(
        "CSRF_TRUSTED_ORIGINS",
        "https://imn-vendoro-55af0b986025.herokuapp.com",
    )
    # HSTS (recommended for production)
    SECURE_HSTS_SECONDS = env_int("SECURE_HSTS_SECONDS", 31536000)  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
        "SECURE_HSTS_INCLUDE_SUBDOMAINS", "1"
    )
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", "1")

# Application definition
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party
    'allauth',
    'allauth.account',
    'cloudinary',
    'cloudinary_storage',

    # ProjectApps
    'home',
    'users',
    'marketplace',
    'orders',
    'payments',
    'admintools',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_USER_MODEL = "users.User"

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Message tags for Bootstrap
MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# allauth config
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_FORMS = {
    "signup": "users.forms.RoleSignupForm",
}

# Email
DEFAULT_FROM_EMAIL = (
    os.environ.get("DEFAULT_FROM_EMAIL")
    or os.environ.get("EMAIL_HOST_USER")
    or "no-reply@vendoro.app"
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL
SUPPORT_EMAIL = os.environ.get("SUPPORT_EMAIL", DEFAULT_FROM_EMAIL)

if os.environ.get("EMAIL_BACKEND"):
    EMAIL_BACKEND = os.environ["EMAIL_BACKEND"]
else:
    if env_bool("DEVELOPMENT", "0"):
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    else:
        EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
        EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
        EMAIL_PORT = env_int("EMAIL_PORT", 587)
        EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", "1")
        EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
        EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASS")
        EMAIL_TIMEOUT = env_int("EMAIL_TIMEOUT", 20)

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'orders.context_processors.cart_count',
                'marketplace.context_processors.cloudinary',
                'marketplace.context_processors.seller_nav',
            ],
        },
    },
]

ROOT_URLCONF = 'vendoro.urls'
WSGI_APPLICATION = 'vendoro.wsgi.application'


# Database
DATABASES = {
   "default": dj_database_url.parse(
        os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        ssl_require=not DEBUG
   )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Cloudinary settings
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get("CLOUDINARY_NAME", ""),
    'API_KEY': os.environ.get("CLOUDINARY_API", ""),
    'API_SECRET': os.environ.get("CLOUDINARY_SECRET", ""),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_NAME", ""),
    api_key=os.environ.get("CLOUDINARY_API", ""),
    api_secret=os.environ.get("CLOUDINARY_SECRET", ""),
    secure=True,
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Stripe settings
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_CURRENCY = os.environ.get("STRIPE_CURRENCY", default="gbp")

# Logging
DEBUG_PROPAGATE_EXCEPTIONS = os.getenv(
    "DEBUG_PROPAGATE_EXCEPTIONS", "1" if DEBUG else "0"
) in {"1", "true", "True"}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
