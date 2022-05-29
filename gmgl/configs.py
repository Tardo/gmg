# GMG Copyright 2022 - Alexandre Díaz
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from gmgl.utils import get_supported_languages
import configparser
import tempfile
import os
from os.path import exists
import gmgl
import binascii


class GMGConfig(object):
    def __init__(self):
        if not exists('gmg.conf'):
            self._generate()

        need_update = False

        config = configparser.ConfigParser()
        config.read_file(open('gmg.conf'))

        self.VERSION = '0.3.2'
        self.UPLOAD_FOLDER = tempfile.mkdtemp()

        self.SECRET_KEY = config.get('global', 'secret', fallback='')
        self.MAX_CONTENT_LENGTH = (
            config.getint('global', 'max_upload_size', fallback=16) * 1024 * 1024
        )
        self.PARTITION = config.get('global', 'partition', fallback='/')
        self.TEMPLATES_AUTO_RELOAD = config.getboolean(
            'global', 'templates_auto_reload'
        )
        self.HOST = config.get('global', 'host', fallback='0.0.0.0')
        self.PORT = config.getint('global', 'port', fallback='8000')
        self.THREADED = config.getboolean('global', 'threaded', fallback=True)
        self.SEND_FILE_MAX_AGE_DEFAULT = config.getint(
            'global', 'default_file_max_age', fallback=31536000
        )
        self.CANONICAL_URL = config.get(
            'global', 'canonical_url', fallback='http://localhost'
        )

        self.ADMIN_USERNAME = config.get('admin', 'username', fallback='admin')
        self.ADMIN_PASSWORD = config.get('admin', 'password', fallback='')

        self.ALLOWED_ORIGINS = config.get(
            'cors', 'allowed_origins', fallback='*'
        ).split(',')

        self.DEBUG = config.getboolean('debug', 'engine')
        self.ASSETS_DEBUG = config.getboolean('debug', 'assets')

        self.CACHE_TYPE = config.get('cache', 'type', fallback='SimpleCache')
        self.CACHE_DEFAULT_TIMEOUT = config.getint(
            'cache', 'default_timeout', fallback=300
        )

        self.SQLALCHEMY_DATABASE_URI = config.get('database', 'uri', fallback='')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = config.getboolean(
            'database', 'track_modifications'
        )
        self.SQLALCHEMY_ECHO = config.getboolean('database', 'echo')
        self.DATABASE_NAME = config.get('database', 'name', fallback='gmg')

        self.LOGFILE = config.get('log', 'file', fallback='gmg.log')
        self.LOGBYTES = config.getint('log', 'maxbytes', fallback=10000)

        self.LOGIN_MAX_TRIES = config.getint('login', 'max_tries', fallback=3)
        self.LOGIN_BAN_TIME = config.getint('login', 'ban_time', fallback=1200)

        self.SESSION_TIME = config.getint('session', 'time', fallback=10)
        self.DEFAULT_TIMEZONE = config.get(
            'session', 'default_timezone', fallback=os.environ.get('TZ', 'UTC')
        )
        self.SESSION_COOKIE_SECURE = config.getboolean(
            'session', 'session_cookie_secure', fallback=False
        )
        self.SESSION_COOKIE_SAMESITE = config.get(
            'session', 'session_cookie_samesite', fallback='Lax'
        )

        self.SSL = config.getboolean('ssl', 'enabled')
        self.PKEY = config.get('ssl', 'pkey', fallback='')
        self.CERT = config.get('ssl', 'cert', fallback='')
        self.SSL = (
            False
            if not os.path.isfile(self.PKEY) or not os.path.isfile(self.CERT)
            else self.SSL
        )

        self.MV_SESSION_HASH = config.get('analyzer', 'mv_session_hash', fallback='')
        self.MV_SCHEDULER_POST_REQUESTS_DELAY = config.getint(
            'analyzer', 'mv_scheduler_post_requests_delay', fallback=2
        )
        self.MV_SCHEDULER_THREAD_REQUESTS_DELAY = config.getint(
            'analyzer', 'mv_scheduler_thread_requests_delay', fallback=3
        )
        self.MV_SCHEDULER_INTERVAL_MINUTES = config.getint(
            'analyzer', 'mv_scheduler_interval_minutes', fallback=5
        )

        self.SCHEDULER_EXECUTORS_WORKERS = config.getint(
            'scheduler', 'executor_workers', fallback=2
        )
        self.SCHEDULER_VIEWS_ENABLED = False
        self.SCHEDULER_EXECUTORS = {
            'default': {
                'type': 'threadpool',
                'max_workers': self.SCHEDULER_EXECUTORS_WORKERS,  # Optimal: Num. physical Cores
            }
        }
        self.SCHEDULER_JOB_DEFAULTS = {
            'coalesce': True,
            'max_instances': 1,
        }

        self.ALLOWED_EXTENSIONS = set(['zip', 'gz', 'png', 'jpg', 'gif'])

        # Override with environment values
        if os.environ.get('GMG_DATABASE_URI'):
            self.SQLALCHEMY_DATABASE_URI = os.environ['GMG_DATABASE_URI']
        if os.environ.get('GMG_SECRET'):
            self.SECRET_KEY = os.environ['GMG_SECRET']
        if os.environ.get('GMG_ADMIN_USERNAME'):
            self.ADMIN_USERNAME = os.environ['GMG_ADMIN_USERNAME']
        if os.environ.get('GMG_ADMIN_PASSWORD'):
            self.ADMIN_PASSWORD = os.environ['GMG_ADMIN_PASSWORD']

        self.SCHEDULER_JOBSTORES = {
            'default': SQLAlchemyJobStore(url=self.SQLALCHEMY_DATABASE_URI)
        }

        self.BABEL_DEFAULT_LOCALE = 'en'
        self.BABEL_DEFAULT_TIMEZONE = 'UTC'
        self.SUPPORT_LANGUAGES = get_supported_languages()

        self.SQLALCHEMY_ENGINE_OPTIONS = {
            'connect_args': {'options': '-c timezone=utc'}
        }

        self.ROLLUP_EXTRA_ARGS = ['-c', 'rollup.config.js']

        # Generate absent hashes
        if not self.SECRET_KEY:
            self.SECRET_KEY = binascii.hexlify(os.urandom(32)).decode()
            config.set('global', 'secret', self.SECRET_KEY)
            need_update = True
        if not self.ADMIN_PASSWORD:
            self.ADMIN_PASSWORD = binascii.hexlify(os.urandom(12)).decode()
            config.set('admin', 'password', self.ADMIN_PASSWORD)
            need_update = True

        if need_update:
            with open('gmg.conf', 'w') as file:
                config.write(file)

    def _generate(self):
        Config = configparser.ConfigParser()

        Config.add_section('global')
        Config.set('global', 'secret', '')
        Config.set('global', 'max_upload_size', '16')
        Config.set('global', 'partition', '/')
        Config.set('global', 'templates_auto_reload', 'false')
        Config.set('global', 'host', '0.0.0.0')
        Config.set('global', 'port', '8000')
        Config.set('global', 'threaded', 'true')
        Config.set('global', 'default_file_max_age', '86400')
        Config.set('global', 'canonical_url', 'http://localhost')

        Config.add_section('admin')
        Config.set('admin', 'username', 'admin')
        Config.set('admin', 'password', '')

        Config.add_section('cors')
        Config.set('cors', 'allowed_origins', '*')

        Config.add_section('debug')
        Config.set('debug', 'engine', 'false')
        Config.set('debug', 'assets', 'false')

        Config.add_section('cache')
        Config.set('cache', 'type', 'SimpleCache')
        Config.set('cache', 'default_timeout', '300')

        Config.add_section('database')
        Config.set('database', 'uri', '')
        Config.set('database', 'track_modifications', 'false')
        Config.set('database', 'echo', 'false')
        Config.set('database', 'name', 'gmg')

        Config.add_section('log')
        Config.set('log', 'file', 'gmg.log')
        Config.set('log', 'maxbytes', '10000')

        Config.add_section('login')
        Config.set('login', 'max_tries', '3')
        Config.set('login', 'ban_time', '1200')

        Config.add_section('session')
        Config.set('session', 'time', '10')
        Config.set('session', 'default_timezone', 'UTC')
        Config.set('session', 'session_cookie_secure', 'false')
        Config.set('session', 'session_cookie_samesite', 'Lax')

        Config.add_section('ssl')
        Config.set('ssl', 'enabled', 'false')
        Config.set('ssl', 'pkey', '')
        Config.set('ssl', 'cert', '')

        Config.add_section('analyzer')
        Config.set('analyzer', 'mv_session_hash', '')
        Config.set('analyzer', 'mv_scheduler_post_requests_delay', '2')
        Config.set('analyzer', 'mv_scheduler_thread_requests_delay', '3')
        Config.set('analyzer', 'mv_scheduler_interval_minutes', '5')

        Config.add_section('scheduler')
        Config.set('scheduler', 'executor_workers', '2')

        with open('gmg.conf', 'w') as file:
            Config.write(file)


class GMGConfigTest(GMGConfig):
    def __init__(self):
        GMGConfig.__init__(self)
        self.WTF_CSRF_ENABLED = False
        self.WTF_CSRF_CHECK_DEFAULT = False
        self.TESTING = True
        self.ASSETS_DEBUG = True
        self.ADMIN_USERNAME = 'admin_test'
        self.ADMIN_PASSWORD = 'pass_test'
