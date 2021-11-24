"""
Django settings for surveykong project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

SETTINGS_PATH = os.path.normpath(os.path.dirname(__file__))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&=_@q@gp_38ijj645c%k#bt&7livtn9!q4m3yp&a4#neqxhfsu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG_FLAG', False)

ALLOWED_HOSTS = [
	'localhost',
	'127.0.0.1',
]

INTERNAL_IPS = ['127.0.0.1',]

# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.admindocs',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.humanize',
	'survey',
	'django_extensions',
	'hijack',
	'hijack.contrib.admin',
	'sslserver',
]

MIDDLEWARE = [
	'middleware.login_required.LoginRequiredMiddleware', # Require auth.
	'django.middleware.security.SecurityMiddleware',
	'whitenoise.middleware.WhiteNoiseMiddleware',
	'django.middleware.gzip.GZipMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'middleware.get_create_uuid.getOrCreateUuid',
	'hijack.middleware.HijackUserMiddleware',
]

ROOT_URLCONF = 'surveykong.urls'

if DEBUG:
	MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
	INSTALLED_APPS.append('debug_toolbar')


TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [
			'templates',
		],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'survey.context_processors.app_settings',
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
			'libraries': {
				'common_templatetags': 'templatetags.common_templatetags'	
			},
		},
	},
]


WSGI_APPLICATION = 'surveykong.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': os.getenv('DJANGO_DB_NAME', 'surveykong'),
		'USER': os.getenv('DJANGO_DB_USER', ''),
		'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', ''),
		'HOST': os.getenv('DJANGO_DB_HOST', 'localhost'),
		'PORT': os.getenv('DJANGO_DB_PORT', 5432),
	}
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

ADMINS = []
MANAGERS = ADMINS
SERVER_EMAIL = ' surveykong-error@somedomain.com'
#EMAIL_HOST = ''

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static-deploy/')

STATICFILES_DIRS = [
	os.path.join(BASE_DIR, "static/"),
]

STATIC_URL = os.getenv('DJANGO_STATIC_URL', '/static-surveykong/')
MEDIA_URL = os.getenv('DJANGO_MEDIA_URL', '/media/')

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Host non-app static files on COS, serve with CDN and prefix URLs with thi
# instead of serving common non-app files with %static%
CDN_FILES_URL = ''

# 1 year session cookie TTL.
SESSION_COOKIE_AGE = 31536000
SESSION_COOKIE_SAMESITE = False
SESSION_COOKIE_SECURE = True


## Note: No custom sign-in/out URL go here. All done via normal app URL and views.

## Django first allows easy dev access via Django and wont error on LDAP for a local user/dev testing.
AUTHENTICATION_BACKENDS = [
	'django.contrib.auth.backends.ModelBackend',
]

# If you want 500 and 404s alerts to go to a slack room, 
#  set the webhook URL as an env var.
SLACK_ALERT_URL = os.getenv('DJANGO_SLACK_ALERT_URL', '')

# If you use COS instead of local static files.
# This is to use COS instead of local storage for static files.
# AWS_ACCESS_KEY_ID = os.getenv('COS_ACCESS_KEY_ID', '')
# AWS_SECRET_ACCESS_KEY = os.getenv('COS_SECRET_ACCESS_KEY', '')
# AWS_S3_HOST = os.getenv('COS_AUTH_ENDPOINT')
# AWS_S3_ENDPOINT_URL = os.getenv('COS_ENDPOINT')
# AWS_LOCATION = 'static'
# AWS_QUERYSTRING_AUTH = False
# AWS_DEFAULT_ACL = 'public-read'
# # Your app specific. Bucket name and CDN url mapped to your bucket.
# AWS_STORAGE_BUCKET_NAME = os.getenv('COS_BUCKET_NAME', '')
# AWS_S3_CUSTOM_DOMAIN = os.getenv('COS_CDN_DOMAIN', '')


#If you use SSO:
# Uses OIDC plugin: https://mozilla-django-oidc.readthedocs.io/en/stable/
# OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ.get('OIDC_OP_AUTHORIZATION_ENDPOINT', '')
# OIDC_OP_TOKEN_ENDPOINT = os.environ.get('OIDC_OP_TOKEN_ENDPOINT', '')
# OIDC_OP_USER_ENDPOINT = os.environ.get('OIDC_OP_USER_ENDPOINT', '')
# OIDC_OP_JWKS_ENDPOINT = os.environ.get('OIDC_OP_JWKS_ENDPOINT', '')
# OIDC_RP_CLIENT_ID = os.environ.get('OIDC_RP_CLIENT_ID', '')
# OIDC_RP_CLIENT_SECRET = os.environ.get('OIDC_RP_CLIENT_SECRET', '')
# OIDC_RP_SIGN_ALGO = os.environ.get('OIDC_RP_SIGN_ALGO', 'RS256')
# OIDC_REDIRECT_FIELD_NAME = 'next'

## This is used when a view requires authentication and needs to redirect the user to the sigin-in page.
LOGIN_URL = '/survey/signin/'
# Use this if using SSO:
#LOGIN_URL = 'oidc_authentication_init'  

#LDAP_URL = ''

# Redirected after hijacking a user.
LOGIN_REDIRECT_URL = '/'

X_FRAME_OPTIONS = 'SAMEORIGIN'
#SECURE_REFERRER_POLICY = 'unsafe-url' # Default: 'same-origin'

DEFAULT_AUTO_FIELD='django.db.models.AutoField'


## Import local settings that may exist to override production settings above.
## (settings_local.py)
try:
	from .local_settings import *
except ImportError:
	pass


if not DEBUG:
	SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
	SECURE_SSL_REDIRECT = True
	
if DEBUG and DATABASES['default']['HOST'] != 'localhost':
	print('##############################\n##\n##  WARNING, YOU ARE USING PRODUCTION DATABASE\n##\n##############################')
