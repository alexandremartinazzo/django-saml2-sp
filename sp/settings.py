import os

import saml2
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED
from saml2.sigver import get_xmlsec_binary

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'not_so_secret_key_for_SP'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangosaml2',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sp.urls'

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

WSGI_APPLICATION = 'sp.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'handlers': {
    'console': {
      'class': 'logging.StreamHandler',
    },
  },
  'loggers': {
    '': {
      'handlers': ['console'],
      'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
    },
  },
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

##############################################################################
# SAML2 Service Provider settings

SESSION_COOKIE_NAME = 'sessionid_sp'

LOGIN_URL = '/saml2/login/'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'djangosaml2.backends.Saml2Backend',
)

SAML_BASE_URL = 'http://localhost:9000/saml2'

SAML_CONFIG = {
    'debug': DEBUG,
    'xmlsec_binary': get_xmlsec_binary(['/usr/bin/xmlsec1']),
    'entityid': '{}/metadata'.format(SAML_BASE_URL),

    'service': {
        'sp': {
            'name': 'Django2 SAML2 SP',
            'endpoints': {
                'assertion_consumer_service': [
                    ('{}/acs/'.format(SAML_BASE_URL), saml2.BINDING_HTTP_POST)
                ],
                'single_sign_on_service': [
                    ('{}/ls/post'.format(SAML_BASE_URL), saml2.BINDING_HTTP_POST),
                    ('{}/ls/redirect'.format(SAML_BASE_URL), saml2.BINDING_HTTP_REDIRECT),
                ],
            },
            'name_id_format': [NAMEID_FORMAT_EMAILADDRESS],
            'authn_requests_signed': True,
            'want_assertions_signed': True,
            'allow_unsolicited': True,
        },
    },

    'attribute_map_dir': os.path.join(BASE_DIR, 'attribute_maps'),
    'metadata': {
        'local': [os.path.join(BASE_DIR, 'metadata/metadata.xml')],
    },

    # Signing
    'key_file': BASE_DIR + '/certificates/private.key',
    'cert_file': BASE_DIR + '/certificates/public.cert',
    # Encryption
    'encryption_keypairs': [{
        'key_file': BASE_DIR + '/certificates/private.key',
        'cert_file': BASE_DIR + '/certificates/public.cert',
    }],
    'valid_for': 365 * 24,
}

SAML_USE_NAME_ID_AS_USERNAME = True
SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'username'
SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP = '__iexact'
SAML_CREATE_UNKNOWN_USER = True

SAML_ATTRIBUTE_MAPPING = {
    # SAML: DJANGO
    # Must also be present in attribute-maps!
    'email': ('email', ),
    'first_name': ('first_name', ),
    'last_name': ('last_name', ),
    'is_staff': ('is_staff', ),
    'is_superuser':  ('is_superuser', ),
}
