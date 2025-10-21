from .base import *

INSTALLED_APPS += ['debug_toolbar', ]

MIDDLEWARE += [

    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_run',
        'HOST': 'localhost',
        'PORT': '5432',
        'USER': 'andrei',
        'PASSWORD': 'be098140a513',
    }
}

INTERNAL_IPS = [
    '127.0.0.1',
    # Add other internal IPs if needed
]
