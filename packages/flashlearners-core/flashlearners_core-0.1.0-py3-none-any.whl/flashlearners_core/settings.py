import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PACKAGE_DIR = Path(__file__).resolve().parent
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

AUTH_USER_MODEL = 'app.User'

SECRET_KEY = os.getenv("SECRET_KEY", "@#$#EKNEak5(^1%s38r*jc3!96)@(#$IURNIO=2-3ny^_x4(l05s")

INSTALLED_APPS = ['daphne']

CORE_APPS = [
    'storages',
    'flashlearners_core',
    'flashlearners_core.app',
]


def db(key):
    return os.getenv(key)


def get_env(key, default=None):
    return os.getenv(key, default)


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': "django.db.backends.sqlite3",
            'NAME': "test.db"
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': db("DB_ENGINE"),
            'NAME': db('DB_NAME'),
            'USER': db('DB_USER'),
            'PASSWORD': db('DB_PASSWORD'),
            'HOST': db('DB_HOST'),
            'PORT': db('DB_PORT'),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


#######################
# LOCALIZATION CONFIG #
#######################
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Lagos'

USE_I18N = True

USE_L10N = True

USE_TZ = True


###############
# MAIL CONFIG #
###############
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_FILE_PATH = os.path.join(PACKAGE_DIR, 'emails')
EMAIL_HOST = 'flashlearners.com'
EMAIL_HOST_USER = get_env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = get_env('DEFAULT_FROM_EMAIL',
                             'Flashlearners<hello@flashlearners.com>')
SERVER_EMAIL = get_env('SERVER_EMAIL')
EMAIL_PORT = 465
# Gmail SMTP port (TLS): 587
# Gmail SMTP port (SSL): 465
EMAIL_USE_TLS = True
EMAIL_SIGNATURE = 'The Flashlearners Team'
ADMINS = (
    ('Fola', 'phourxx0001@gmail.com'),
)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

#################
# LOGGER CONFIG #
#################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s] %(asctime)s %(name)s: %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'root': {
        'handlers': ['console', ],
        'level': 'DEBUG'
    },
    'loggers': {
        'django.request': {
            'handlers': [
                'console', 'mail_admins'
            ],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}

CORS_ALLOW_ALL_ORIGINS = True

####################
# ONESIGNAL CONFIG #
####################
ONE_SIGNAL_APP_ID = get_env("ONE_SIGNAL_APP_ID")
ONE_SIGNAL_REST_API_KEY = get_env("ONE_SIGNAL_REST_API_KEY")
ONE_SIGNAL_USER_AUTH_KEY = get_env("ONE_SIGNAL_USER_AUTH_KEY")

################
# MEDIA CONFIG #
################
FILE_UPLOAD_STORAGE = get_env("FILE_UPLOAD_STORAGE", default="s3")  # gcloud | s3

MEDIA_ROOT_NAME = "media"
MEDIA_ROOT = os.path.join(os.getenv('MEDIA_ROOT', '/'), MEDIA_ROOT_NAME)
MEDIA_URL = f"/{MEDIA_ROOT_NAME}/"
STATIC_URL = '/static/'
STATIC_ROOT = PACKAGE_DIR / 'static/'

if FILE_UPLOAD_STORAGE == "s3":
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    # Using django-storages
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_AUTO_CREATE_BUCKET = True
    AWS_S3_ACCESS_KEY_ID = get_env("AWS_S3_ACCESS_KEY_ID")
    AWS_S3_SECRET_ACCESS_KEY = get_env("AWS_S3_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = get_env("AWS_STORAGE_BUCKET_NAME",
                                      "flashlearnersapp")
    AWS_S3_REGION_NAME = get_env("AWS_S3_REGION_NAME")
    # AWS_S3_SIGNATURE_VERSION = get_env("AWS_S3_SIGNATURE_VERSION", default="s3v4")

    # https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html#canned-acl
    # AWS_DEFAULT_ACL = get_env("AWS_DEFAULT_ACL", default="public-read")

    # AWS_PRESIGNED_EXPIRY = int(get_env("AWS_PRESIGNED_EXPIRY", default='10'))  # seconds

if FILE_UPLOAD_STORAGE == "gcloud":
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = get_env("GS_BUCKET_NAME")
    STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_DEFAULT_ACL = "publicRead"

customColorPalette = [
    {
        'color': 'hsl(4, 90%, 58%)',
        'label': 'Red'
    },
    {
        'color': 'hsl(340, 82%, 52%)',
        'label': 'Pink'
    },
    {
        'color': 'hsl(291, 64%, 42%)',
        'label': 'Purple'
    },
    {
        'color': 'hsl(262, 52%, 47%)',
        'label': 'Deep Purple'
    },
    {
        'color': 'hsl(231, 48%, 48%)',
        'label': 'Indigo'
    },
    {
        'color': 'hsl(207, 90%, 54%)',
        'label': 'Blue'
    },
]

CKEDITOR_5_CONFIGS = {
    # 'default': {
    #     'toolbar': ['heading', '|', 'bold', 'italic', 'link',
    #                 'bulletedList', 'numberedList', 'blockQuote',
    #                 'imageUpload', ],
    # },
    'default': {
        'max-height': '500px',
        # 'width': '500px',
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic',
                    'link', 'underline', 'strikethrough',
                    'code', 'subscript', 'superscript', 'highlight', '|',
                    'insertImage', 'bulletedList', 'numberedList',
                    'todoList', '|',
                    'codeBlock', 'sourceEditing', 'blockQuote', '|',
                    'fontSize', 'fontFamily', 'fontColor',
                    'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable', ],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter',
                        'imageStyle:side', '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                               'tableProperties', 'tableCellProperties'],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph',
                 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1',
                 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2',
                 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3',
                 'class': 'ck-heading_heading3'}
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}
