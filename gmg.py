# GMG Copyright 2022 - Alexandre Díaz
import re
import os
import signal
import pytz
import fcntl
import atexit
import logging
from datetime import datetime, date
from flask import (
    Flask,
    request,
    session,
    g,
    redirect,
    url_for,
    abort,
    flash,
    current_app,
    Blueprint,
)
from sqlalchemy import func, desc
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask_babel import _, format_datetime
from flask_assets import Bundle
from webassets.filter import register_filter
from webassets_rollup import Rollup
from flask_csp.csp import csp_default
from tools.banned_list import BannedList
from gmgl.nlp.spacy import spacy_nlp
from gmgl.nlp.knowledge import get_analyzer_sections
from gmgl.json_encoder import GMGJSONEncoder
from gmgl.sqlalchemy.xml_loader import load_xml_records
from gmgl.sqlalchemy.database import db, db_get_active_user, db_get_engine_name
from gmgl.sqlalchemy.models import get_db_env
from gmgl.sqlalchemy.models.internal import Site, AppWebConfig
from gmgl.utils import (
    get_session_timezone,
    is_session_expired,
    get_url_filename_format,
    date_to_str,
    gen_sha256_from_string,
)
from gmgl.analyzers.mv import start_analyze as mv_analyze

_logger = logging.getLogger(__name__)

#################################
# FLASK GENERAL
#################################
register_filter(Rollup)
BANLIST = BannedList()
h = csp_default()
h.update(
    {
        'img-src': "'self' data: w3.org",
    }
)

gmg = Blueprint('gmg', __name__, static_folder='static/')

from gmgl.addons import *
from routes import *
from cli import *


def create_bundles(mode: str) -> dict:
    bundles = {}
    if 'app_css' not in assets:
        bundles['app_css'] = Bundle(
            'gmg/css/*.css',
            output=f"gmg/dist/app{'' if mode == 'production' else '.min'}.css",
            filters='postcss',
        )
    if 'app_js' not in assets:
        bundles['app_js'] = Bundle(
            'gmg/js/main.js',
            output=f"gmg/dist/app{'' if mode == 'production' else '.min'}.js",
            filters='rollup',
        )
    return bundles


def register_bundles(assets, bundles: dict):
    for bundle_name in bundles:
        bundle_obj = bundles[bundle_name]
        assets.register(bundle_name, bundle_obj)
        bundle_obj.build()


def _print_app_info(app):
    db_env = get_db_env()
    routes_count = sum(1 for _ in app.url_map.iter_rules())
    _logger.info(f' * Using {db_get_engine_name()} as database engine')
    _logger.info(f' * {len(db_env)} models loaded')
    _logger.info(f' * {routes_count} routes defined')

def _auto_install():
    db.create_all()
    processed_ids = load_xml_records(
        os.path.join(Path(__file__).resolve().parent, 'data', 'records.xml'),
        igroup='base',
    )
    if processed_ids:
        AppWebConfig.set_param('version', current_app.config['VERSION'])
        db.session.commit()

def initialize_once(app):
    f = open('gmg.lock', 'wb')
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

        # Auto-Install base data
        has_base_tables = bool(db.session.execute(
            "SELECT count(*) FROM pg_catalog.pg_tables WHERE tablename = 'app_web_config'"
        ).first()[0])
        if not has_base_tables:
            _auto_install()

        # spaCy NLP
        spacy_nlp.init_app(app)

        # APScheduler
        scheduler.init_app(app)
        scheduler.remove_all_jobs()
        scheduler.add_job(
            'gmg:mv_analyze',
            mv_analyze,
            trigger='interval',
            minutes=app.config['MV_SCHEDULER_INTERVAL_MINUTES'],
            replace_existing=True,
        )
        scheduler.start()
        atexit.register(scheduler.shutdown)

        _print_app_info(app)
    except Exception as err:
        pass

    def unlock():
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()

    atexit.register(unlock)


# Create Flask App
def create_app(gmgconf):
    _logger.info('Initializing GMG app...')
    app = Flask(__name__)
    app.config.from_object(gmgconf)
    app.register_blueprint(gmg)
    app.json_encoder = GMGJSONEncoder
    cache.init_app(app)
    assets.app = app
    assets.init_app(app)
    bundles = create_bundles(app.env)
    register_bundles(assets, bundles)
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app)
    babel_js.init_app(app)
    cors.init_app(app, origins=app.config['ALLOWED_ORIGINS'])
    csrf.init_app(app)
    compress.init_app(app)

    # Ensure app timezone
    db_user = db_get_active_user()
    db.session.execute(f"ALTER USER {db_user} SET timezone='UTC'")
    db.session.execute("SET TIME ZONE 'UTC'")

    initialize_once(app)

    @babel.localeselector
    def get_locale():
        try:
            return request.accept_languages.best_match(
                current_app.config['SUPPORT_LANGUAGES']
            )
        except RuntimeError:
            return 'en'

    @babel.timezoneselector
    def get_timezone():
        return get_session_timezone()

    return app


#################################
# FLASK CALLBACKS
#################################
@gmg.context_processor
def utility_processor():
    def get_app_config():
        return AppWebCoSfig.query.get(1)

    def get_timezones():
        return pytz.all_timezones

    def get_session_time():
        dt = datetime.utcnow()
        return {
            'localtime': format_datetime(dt, 'short'),
            'localzone': format_datetime(dt, 'z'),
        }

    def get_post_url(thread_url, post_ref_id):
        if g.active_site.ref == 'mediavida':
            page_num = int(post_ref_id / g.active_site.post_per_page) + 1
            return f'{g.active_site.url}{thread_url}/{page_num}#{post_ref_id}'
        return thread_url

    def now():
        return datetime.utcnow()

    return dict(
        get_app_config=get_app_config,
        format_datetime=format_datetime,
        get_session_time=get_session_time,
        get_url_filename_format=get_url_filename_format,
        date_to_str=date_to_str,
        get_post_url=get_post_url,
        gen_sha256_from_string=gen_sha256_from_string,
        now=now,
    )


@gmg.before_request
def before_request():
    # Session Banned?
    BANLIST.refresh()
    if not request.path.startswith('/banned') and BANLIST.find(request.remote_addr):
        abort(403)

    # Session Expired?
    if is_session_expired():
        flash(_('Session timed out!'), 'info')
        redirect('/logout')

    # Check site
    if not session.get('site_id'):
        session['site_id'] = Site.query.first().id

    # Base data
    g.active_site = Site.get_session_active_site()
    g.canonical_base_url = current_app.config['CANONICAL_URL']


# @gmg.teardown_request
# def teardown_request(exception):
