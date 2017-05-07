"""
Local settings of current environment
"""
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tim_database',
        'USER': 'devtim',
        'PASSWORD': 'timcollegetwilio2017',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}