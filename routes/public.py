# GMG Copyright 2022 - Alexandre Díaz
from gmg import gmg, csrf, BANLIST
import time
import json
import pytz
import base64
from io import BytesIO
from pytz import timezone
from datetime import datetime, timedelta
from flask import (
    abort,
    current_app,
    flash,
    g,
    jsonify,
    make_response,
    request,
    redirect,
    render_template,
    session,
    send_file,
    url_for,
)
from flask_babel import Babel, _, format_datetime
from flask_csp.csp import csp_header
from sqlalchemy import or_, func, desc
from sqlalchemy.ext.serializer import dumps
from flask_sqlalchemy_caching import FromCache
from tools.banner_generator import BannerGenerator
from gmgl.addons import cache
from gmgl.sqlalchemy.database import db
from gmgl.sqlalchemy.models import RecordMetadata
from gmgl.sqlalchemy.models.internal import Attachment
from gmgl.sqlalchemy.models.analyzer import (
    AnalyzerUser,
    AnalyzerPost,
    AnalyzerPostComment,
    AnalyzerPostMedia,
    AnalyzerPostStat,
    AnalyzerThread,
    AnalyzerWebEvent,
    MediaType,
    rel_analyzer_post_analyzer_post_stat,
    rel_analyzer_user_analyzer_post_stat,
)
from gmgl.utils import (
    flash_errors,
    get_session_timezone,
    get_url_filename_format,
    get_session_login_tries,
    get_linux_distribution,
    PUBLIC_IP,
    check_referrer,
    date_to_str,
    str_db_to_date,
    time_to_str,
    GMG_DATABASE_DATE_FORMAT,
    GMG_DATE_FORMAT,
    GMG_DATETIME_FORMAT,
)
from gmgl.nlp.knowledge import get_analyzer_sections
from werkzeug.security import check_password_hash, generate_password_hash
import logging

_logger = logging.getLogger(__name__)


#################################
# TOOLS
#################################
def get_site_status():
    site_id = g.active_site.id
    today = datetime.utcnow()
    results = {'today': _('Undefined'), 'week': _('Undefined'), 'month': _('Undefined')}
    # Today
    startday = today.replace(hour=0, minute=0, second=0)
    post_count = AnalyzerPost.query.filter(
        AnalyzerPost.site_id == site_id, AnalyzerPost.date >= startday
    ).count()
    stats_today = (
        db.session.query(
            func.sum(AnalyzerPostStat.insult_word_count),
            func.sum(AnalyzerPostStat.swear_word_count),
            func.sum(AnalyzerPostStat.good_word_count),
            func.sum(AnalyzerPostStat.laugh_word_count),
            func.sum(AnalyzerPostStat.love_word_count),
            func.sum(AnalyzerPostStat.sad_word_count),
            func.sum(AnalyzerPostStat.dead_word_count),
            func.sum(AnalyzerPostStat.sex_word_count),
        )
        .join(AnalyzerPost, isouter=True)
        .filter(AnalyzerPost.site_id == site_id, AnalyzerPost.date >= startday)
        .first()
    )
    if any(stats_today):
        today_total = sum(list(stats_today))
        today_results = [
            stats_today[0] / today_total,  # toxic
            stats_today[1] / today_total,  # rude
            (stats_today[2] + stats_today[3]) / today_total,  # confortable
            stats_today[4] / today_total,  # in_love
            stats_today[5] / today_total,  # sad
            stats_today[6] / today_total,  # dead
            stats_today[7] / today_total,  # horny
        ]
        if all(elem == today_results[0] for elem in today_results):
            results['today'] = _('Harmony')
        else:
            analyzer_sections = get_analyzer_sections()
            today_max = max(today_results)
            results['today'] = analyzer_sections[
                2 if today_max == 0.0 else today_results.index(today_max)
            ]
    else:
        results['today'] = _('No Activity')
    # Week
    startday = (today - timedelta(days=today.weekday())).replace(
        hour=0, minute=0, second=0
    )
    post_count = AnalyzerPost.query.filter(
        AnalyzerPost.site_id == site_id, AnalyzerPost.date >= startday
    ).count()
    stats_week = (
        db.session.query(
            func.sum(AnalyzerPostStat.insult_word_count),
            func.sum(AnalyzerPostStat.swear_word_count),
            func.sum(AnalyzerPostStat.good_word_count),
            func.sum(AnalyzerPostStat.laugh_word_count),
            func.sum(AnalyzerPostStat.love_word_count),
            func.sum(AnalyzerPostStat.sad_word_count),
            func.sum(AnalyzerPostStat.dead_word_count),
            func.sum(AnalyzerPostStat.sex_word_count),
        )
        .join(AnalyzerPost, isouter=True)
        .filter(AnalyzerPost.site_id == site_id, AnalyzerPost.date >= startday)
        .first()
    )
    if any(stats_week):
        week_total = sum(list(stats_week))
        week_results = [
            stats_week[0] / week_total,  # toxic
            stats_week[1] / week_total,  # rude
            (stats_week[2] + stats_week[3]) / week_total,  # confortable
            stats_week[4] / week_total,  # in_love
            stats_week[5] / week_total,  # sad
            stats_week[6] / week_total,  # dead
            stats_week[7] / week_total,  # horny
        ]
        if all(elem == week_results[0] for elem in week_results):
            results['week'] = _('Harmony')
        else:
            analyzer_sections = get_analyzer_sections()
            week_max = max(week_results)
            results['week'] = analyzer_sections[
                2 if week_max == 0.0 else week_results.index(week_max)
            ]
    else:
        results['week'] = _('No Activity')
    # Month
    startday = today.replace(day=1, hour=0, minute=0, second=0)
    post_count = AnalyzerPost.query.filter(
        AnalyzerPost.site_id == site_id, AnalyzerPost.date >= startday
    ).count()
    stats_month = (
        db.session.query(
            func.sum(AnalyzerPostStat.insult_word_count),
            func.sum(AnalyzerPostStat.swear_word_count),
            func.sum(AnalyzerPostStat.good_word_count),
            func.sum(AnalyzerPostStat.laugh_word_count),
            func.sum(AnalyzerPostStat.love_word_count),
            func.sum(AnalyzerPostStat.sad_word_count),
            func.sum(AnalyzerPostStat.dead_word_count),
            func.sum(AnalyzerPostStat.sex_word_count),
        )
        .join(AnalyzerPost, isouter=True)
        .filter(AnalyzerPost.site_id == site_id, AnalyzerPost.date >= startday)
        .first()
    )
    if any(stats_month):
        month_total = sum(list(stats_month))
        month_results = [
            stats_month[0] / month_total,  # toxic
            stats_month[1] / month_total,  # rude
            (stats_month[2] + stats_month[3]) / month_total,  # confortable
            stats_month[4] / month_total,  # in_love
            stats_month[5] / month_total,  # sad
            stats_month[6] / month_total,  # dead
            stats_month[7] / month_total,  # horny
        ]
        if all(elem == month_results[0] for elem in month_results):
            results['month'] = _('Harmony')
        else:
            analyzer_sections = get_analyzer_sections()
            month_max = max(month_results)
            results['month'] = analyzer_sections[
                2 if month_max == 0.0 else month_results.index(month_max)
            ]
    else:
        results['month'] = _('No Activity')
    return results


#################################
# GET
#################################
@gmg.route('/', methods=['GET'])
@csp_header()
@cache.cached()
def overview():
    g.canonical_url = '/'
    session['prev_url'] = request.path
    return render_template(
        'pages/index.html.j2',
        dist=get_linux_distribution(),
        ip=PUBLIC_IP,
        site_status=get_site_status(),
    )


@gmg.route('/reports', methods=['GET'])
@csp_header()
@cache.cached()
def reports():
    g.canonical_url = '/reports'
    session['prev_url'] = request.path
    site_id = session.get('site_id')
    # General Section
    general_total_users = AnalyzerUser.query.filter(
        AnalyzerUser.site_id == site_id,
    ).count()
    general_total_posts = AnalyzerPost.query.filter(
        AnalyzerPost.site_id == site_id,
    ).count()
    general_total_threads = AnalyzerThread.query.filter(
        AnalyzerThread.site_id == site_id,
    ).count()
    general_total_medias = (
        AnalyzerPostMedia.query.filter(
            AnalyzerPost.site_id == site_id,
        )
        .join(AnalyzerPost, AnalyzerPost.id == AnalyzerPostMedia.post_id, isouter=True)
        .count()
    )
    wet_online_users = RecordMetadata.ref('base_web_event_type_online_users')
    web_events = (
        AnalyzerWebEvent.query.filter(
            AnalyzerWebEvent.site_id == site_id,
        )
        .order_by(AnalyzerWebEvent.create_date.desc())
        .limit(1000)
        .all()
    )
    return render_template(
        'pages/reports.html.j2',
        general_total_users=general_total_users,
        general_total_posts=general_total_posts,
        general_total_threads=general_total_threads,
        general_total_medias=general_total_medias,
        web_events=web_events,
    )


@gmg.route('/multimedia', methods=['GET'])
@csp_header(
    {
        'img-src': '* data: w3.org',
        'frame-src': 'https://www.youtube.com',
        'child-src': 'https://www.youtube.com',
    }
)
@cache.cached()
def multimedia():
    g.canonical_url = '/multimedia'
    session['prev_url'] = request.path
    site_id = session.get('site_id')
    top10_week_youtube = AnalyzerPostMedia.getTopWeekByType(site_id, 'youtube', 10)
    last_youtube = AnalyzerPostMedia.getLastByType(site_id, 'youtube', 5)
    top10_week_soundcloud = AnalyzerPostMedia.getTopWeekByType(
        site_id, 'soundcloud', 10
    )
    last_soundcloud = AnalyzerPostMedia.getLastByType(site_id, 'soundcloud', 5)
    top10_week_twitter = AnalyzerPostMedia.getTopWeekByType(site_id, 'twitter', 10)
    last_twitter = AnalyzerPostMedia.getLastByType(site_id, 'twitter', 5)
    top10_week_image = AnalyzerPostMedia.getTopWeekByType(site_id, 'image', 10)
    last_image = AnalyzerPostMedia.getLastByType(site_id, 'image', 5)
    return render_template(
        'pages/multimedia.html.j2',
        top10_week_youtube=top10_week_youtube,
        last_youtube=last_youtube,
        top10_week_soundcloud=top10_week_soundcloud,
        last_soundcloud=last_soundcloud,
        top10_week_twitter=top10_week_twitter,
        last_twitter=last_twitter,
        top10_week_image=top10_week_image,
        last_image=last_image,
    )


@gmg.route('/users', methods=['GET'])
@csp_header()
@cache.cached()
def users():
    g.canonical_url = '/users'
    session['prev_url'] = request.path
    site_id = session.get('site_id')
    return render_template(
        'pages/users.html.j2',
        most_active_users_post=AnalyzerPost.getMostMonthActiveUsers(
            site_id=site_id, limit=9
        ),
        new_users=AnalyzerUser.getNewUsers(site_id=site_id, limit=9),
        banned=AnalyzerUser.getBannedUsers(site_id=site_id, limit=9),
        deleted=AnalyzerUser.getDeletedUsers(site_id=site_id, limit=9),
        moderators=AnalyzerUser.getModeratorUsers(site_id=site_id, days=7),
    )


@gmg.route('/users/<string:username>', methods=['GET'])
@csp_header({'frame-src': 'https://streamable.com/'})
@cache.cached()
def user(username):
    g.canonical_url = '/users/{}'.format(username)
    session['prev_url'] = request.path
    site_id = session.get('site_id')
    user = AnalyzerUser.getByName(site_id, username)
    first_post = user and AnalyzerPost.getFirstByUser(site_id, user.id)
    last_post = user and AnalyzerPost.getLastByUser(site_id, user.id)
    post_count = user and AnalyzerPost.getCountByUser(site_id, user.id)
    interactions = user and AnalyzerPost.getMentionsMonthByUser(site_id, user.id)
    post_threads = user and AnalyzerPost.getTopThreadsByUser(
        site_id, user.id, with_last_post=True
    )
    web_events = (
        AnalyzerWebEvent.query.filter(
            AnalyzerWebEvent.site_id == site_id,
            or_(AnalyzerUser.id == user.id, AnalyzerWebEvent.user_id == user.id),
        )
        .join(
            AnalyzerPost,
            AnalyzerPost.id == AnalyzerWebEvent.origin_post_id,
            isouter=True,
        )
        .join(AnalyzerUser, AnalyzerUser.id == AnalyzerPost.author_id, isouter=True)
        .order_by(AnalyzerWebEvent.create_date.desc())
        .limit(1000)
        .all()
    )
    return render_template(
        'pages/user.html.j2',
        user=user,
        first_post=first_post,
        last_post=last_post,
        post_count=post_count,
        interactions=interactions,
        post_threads=post_threads,
        web_events=web_events,
    )


@gmg.route('/search', methods=['GET'])
@csp_header()
def search():
    g.canonical_url = '/search'
    session['prev_url'] = request.path
    site_id = session.get('site_id')
    from gmgl.forms import GeneralSearchForm

    search_form = GeneralSearchForm(request.args, meta={'csrf': False})
    searchterm = request.args.get('term', '')
    users = None
    threads = None
    if search_form.validate():
        sk = '%%%s%%' % searchterm
        # Users
        users = AnalyzerUser.query.filter(
            AnalyzerUser.site_id == site_id, AnalyzerUser.name.ilike(sk)
        ).all()
        # Thread
        threads = AnalyzerThread.query.filter(
            AnalyzerThread.site_id == site_id, AnalyzerThread.title.ilike(sk)
        ).all()
        if len(users) == 1 and users[0].name == searchterm and len(threads) == 0:
            return user(users[0].name)
    if searchterm:
        flash_errors(search_form)
    return render_template(
        'pages/search.html.j2',
        search_form=search_form,
        searchterm=searchterm,
        users=users,
        threads=threads,
    )


@gmg.route('/login', methods=['GET', 'POST'])
@csp_header()
def login():
    g.canonical_url = '/login'
    if (
        not BANLIST.find(request.remote_addr)
        and get_session_login_tries() >= current_app.config['LOGIN_MAX_TRIES']
    ):
        BANLIST.add(request.remote_addr, current_app.config['LOGIN_BAN_TIME'])
        session['login_try'] = 0
        abort(403)

    from gmgl.forms import LoginForm

    login_form = LoginForm()

    if request.method == 'POST':
        if login_form.validate_on_submit():
            request_username = request.form['username']
            request_passwd = request.form['password']
            current_url = (
                session['prev_url']
                if 'prev_url' in session
                else url_for('gmg.overview')
            )
            if (
                current_app.config['ADMIN_USERNAME']
                and current_app.config['ADMIN_PASSWORD']
                and request_username == current_app.config['ADMIN_USERNAME']
                and request_passwd == current_app.config['ADMIN_PASSWORD']
            ):
                session['logged_in'] = True
                session['last_activity'] = int(time.time())
                session['username'] = current_app.config['ADMIN_USERNAME']
                session['is_admin'] = True
                session['timezone'] = False  # Default config
                session['server_formats'] = {
                    'date': GMG_DATE_FORMAT,
                    'datetime': GMG_DATETIME_FORMAT,
                }
                flash(_('You are logged in!'), 'success')

                if current_url == url_for('gmg.login'):
                    return redirect(url_for('gmg.overview'))
                return redirect(current_url)

            session['login_try'] = get_session_login_tries() + 1
            session['last_login_try'] = int(time.time())
            flash(
                _('Invalid username or password! ({0}/{1})').format(
                    get_session_login_tries(), current_app.config['LOGIN_MAX_TRIES']
                ),
                'danger',
            )
    flash_errors(login_form)
    return render_template('pages/login.html.j2', login_form=login_form)


@gmg.route('/logout', methods=['GET'])
@csp_header()
def logout():
    g.canonical_url = '/logout'
    #     current_url = session['prev_url'] if 'prev_url' in session else url_for('gmg.overview')
    session.clear()
    flash(_('You are logged out!'), 'success')
    return redirect(url_for('gmg.overview'))


@gmg.route('/bin/avatar/<string:hash_ref>', methods=['GET'])
@check_referrer()
def bin_avatar_file(hash_ref):
    if hash_ref == 'lazy':
        return redirect('/static/img/default_avatar_low.png')
    elif hash_ref == '0':
        return redirect('/static/img/default_avatar.png')
    attachment_avatar = (
        Attachment.query.options(FromCache(cache)).filter_by(hash_ref=hash_ref).first()
    )
    return send_file(
        BytesIO(attachment_avatar.data), mimetype=attachment_avatar.mimetype
    )


#################################
# POST
#################################
@gmg.route('/_refresh_host_localtime', methods=['POST'])
def refresh_host_localtime():
    """Heartbeat. Thanks to this we can know the number of active users in the page"""
    dt = datetime.utcnow()
    return jsonify(
        {
            'localtime': format_datetime(dt, 'short'),
            'localzone': format_datetime(dt, 'z'),
        }
    )


@gmg.route('/_set_dark_theme', methods=['POST'])
def set_dark_theme():
    request_data = request.get_json(silent=True)
    session['dark_theme'] = request_data.get('enable')
    return jsonify({'success': True})


@gmg.route('/_set_timezone', methods=['POST'])
def set_timezone():
    request_data = request.get_json(silent=True)
    tzstr = request_data.get('tzstr')
    if not tzstr or tzstr not in pytz.all_timezones:
        return jsonify({'error': True, 'errormsg': _('Invalid TimeZone!')})
    session['timezone'] = tzstr
    return jsonify({'success': True})


def _get_chart_data_activity_7d(site_id):
    today = datetime.utcnow()
    startday = (today - timedelta(days=6)).replace(hour=0, minute=0, second=0)
    # Initial values
    chart_data = {'labels': [], 'values': {}}
    chart_data['labels'] = [
        date_to_str(startday + timedelta(days=nday), babel=True) for nday in range(7)
    ]
    chart_data['values'] = {
        'posts': [0] * len(chart_data['labels']),
        'users': [0] * len(chart_data['labels']),
        'mentions': [0] * len(chart_data['labels']),
        'replies': [0] * len(chart_data['labels']),
        'medias': [0] * len(chart_data['labels']),
    }
    # Fill with database values
    posts = (
        db.session.query(
            func.to_char(
                func.timezone(get_session_timezone(), AnalyzerPost.date),
                f'{GMG_DATABASE_DATE_FORMAT} HH24',
            ).label('date_day_hour'),
            func.count(AnalyzerPost.id),
            func.count(func.distinct(AnalyzerPost.author_id)),
            func.count(rel_analyzer_post_analyzer_post_stat.c.analyzer_post_id),
            func.count(rel_analyzer_user_analyzer_post_stat.c.analyzer_user_id),
            func.count(AnalyzerPostMedia.url),
        )
        .join(
            AnalyzerPostStat, AnalyzerPostStat.post_id == AnalyzerPost.id, isouter=True
        )
        .join(
            rel_analyzer_post_analyzer_post_stat,
            rel_analyzer_post_analyzer_post_stat.c.analyzer_post_stat_id
            == AnalyzerPostStat.id,
            isouter=True,
        )
        .join(
            rel_analyzer_user_analyzer_post_stat,
            rel_analyzer_user_analyzer_post_stat.c.analyzer_post_stat_id
            == AnalyzerPostStat.id,
            isouter=True,
        )
        .join(
            AnalyzerPostMedia,
            AnalyzerPostMedia.post_id == AnalyzerPost.id,
            isouter=True,
        )
        .filter(AnalyzerPost.site_id == site_id, AnalyzerPost.date >= startday)
        .group_by('date_day_hour')
        .order_by('date_day_hour')
        .all()
    )
    for post in posts:
        fdate = date_to_str(
            str_db_to_date(f'{post[0]}:00:00', hours=True, tz=get_session_timezone()),
            babel=True,
        )
        try:
            index = chart_data['labels'].index(fdate)
            chart_data['values']['posts'][index] += post[1]
            chart_data['values']['users'][index] += post[2]
            chart_data['values']['replies'][index] += post[3]
            chart_data['values']['mentions'][index] += post[4]
            chart_data['values']['medias'][index] += post[5]
        except:
            pass
    return chart_data


def _get_chart_data_activity_24h(site_id):
    today = datetime.utcnow()
    startday = (today - timedelta(hours=23, minutes=59, seconds=59)).replace(
        minute=0, second=0
    )
    # Initial value
    chart_data = {'labels': [], 'values': {}}
    available_dates = [
        date_to_str(startday + timedelta(hours=nhour), hours=True, babel=True)
        for nhour in range(25)
    ]
    chart_data['labels'] = [
        f'{date_to_str(startday + timedelta(hours=nhour), hours=True, babel=True)} - {time_to_str(startday + timedelta(hours=nhour+1), babel=True)}'
        for nhour in range(25)
    ]
    chart_data['values'] = {
        'posts': [0] * len(chart_data['labels']),
        'users': [0] * len(chart_data['labels']),
        'mentions': [0] * len(chart_data['labels']),
        'replies': [0] * len(chart_data['labels']),
        'medias': [0] * len(chart_data['labels']),
    }
    # Fill with database values
    posts = (
        db.session.query(
            func.to_char(
                func.timezone(get_session_timezone(), AnalyzerPost.date),
                f'{GMG_DATABASE_DATE_FORMAT} HH24',
            ).label('date_day_hour'),
            func.count(AnalyzerPost.id),
            func.count(func.distinct(AnalyzerPost.author_id)),
            func.count(rel_analyzer_post_analyzer_post_stat.c.analyzer_post_id),
            func.count(rel_analyzer_user_analyzer_post_stat.c.analyzer_user_id),
            func.count(AnalyzerPostMedia.url),
        )
        .join(
            AnalyzerPostStat, AnalyzerPostStat.post_id == AnalyzerPost.id, isouter=True
        )
        .join(AnalyzerUser, AnalyzerUser.id == AnalyzerPost.author_id, isouter=True)
        .join(
            rel_analyzer_post_analyzer_post_stat,
            rel_analyzer_post_analyzer_post_stat.c.analyzer_post_stat_id
            == AnalyzerPostStat.id,
            isouter=True,
        )
        .join(
            rel_analyzer_user_analyzer_post_stat,
            rel_analyzer_user_analyzer_post_stat.c.analyzer_post_stat_id
            == AnalyzerPostStat.id,
            isouter=True,
        )
        .join(
            AnalyzerPostMedia,
            AnalyzerPostMedia.post_id == AnalyzerPost.id,
            isouter=True,
        )
        .filter(AnalyzerPost.site_id == site_id, AnalyzerPost.date >= startday)
        .group_by('date_day_hour')
        .order_by('date_day_hour')
        .all()
    )
    for post in posts:
        fdate = date_to_str(
            str_db_to_date(f'{post[0]}:00:00', hours=True, tz=get_session_timezone()),
            hours=True,
            babel=True,
        )
        try:
            index = available_dates.index(fdate)
            chart_data['values']['posts'][index] = post[1]
            chart_data['values']['users'][index] = post[2]
            chart_data['values']['replies'][index] = post[3]
            chart_data['values']['mentions'][index] = post[4]
            chart_data['values']['medias'][index] = post[5]
        except:
            pass
    return chart_data


def _get_chart_data_user_activity_7d(site_id, user_id):
    today = datetime.utcnow()
    startday = (today - timedelta(days=6)).replace(hour=0, minute=0, second=0)
    # Initial values
    chart_data = {'labels': [], 'values': {}}
    chart_data['labels'] = [
        date_to_str(startday + timedelta(days=nday), babel=True) for nday in range(7)
    ]
    chart_data['values'] = {
        'posts': [0] * len(chart_data['labels']),
        'threads': [0] * len(chart_data['labels']),
        'mentions': [0] * len(chart_data['labels']),
        'replies': [0] * len(chart_data['labels']),
        'medias': [0] * len(chart_data['labels']),
    }
    # Fill with database values
    posts = (
        db.session.query(
            func.to_char(
                func.timezone(get_session_timezone(), AnalyzerPost.date),
                f'{GMG_DATABASE_DATE_FORMAT} HH24',
            ).label('date_day_hour'),
            func.count(AnalyzerPost.id),
            func.count(func.distinct(AnalyzerThread.id)),
            func.count(rel_analyzer_post_analyzer_post_stat.c.analyzer_post_id),
            func.count(rel_analyzer_user_analyzer_post_stat.c.analyzer_user_id),
            func.count(AnalyzerPostMedia.url),
        )
        .join(
            AnalyzerThread,
            AnalyzerThread.id == AnalyzerPost.thread_id,
        )
        .join(
            AnalyzerPostStat, AnalyzerPostStat.post_id == AnalyzerPost.id, isouter=True
        )
        .join(AnalyzerUser, AnalyzerUser.id == AnalyzerPost.author_id, isouter=True)
        .join(
            rel_analyzer_post_analyzer_post_stat,
            rel_analyzer_post_analyzer_post_stat.c.analyzer_post_stat_id
            == AnalyzerPostStat.id,
            isouter=True,
        )
        .join(
            rel_analyzer_user_analyzer_post_stat,
            rel_analyzer_user_analyzer_post_stat.c.analyzer_post_stat_id
            == AnalyzerPostStat.id,
            isouter=True,
        )
        .join(
            AnalyzerPostMedia,
            AnalyzerPostMedia.post_id == AnalyzerPost.id,
            isouter=True,
        )
        .filter(
            AnalyzerPost.site_id == site_id,
            AnalyzerPost.author_id == user_id,
            AnalyzerPost.date >= startday,
        )
        .group_by('date_day_hour')
        .order_by('date_day_hour')
        .all()
    )
    for post in posts:
        fdate = date_to_str(
            str_db_to_date(f'{post[0]}:00:00', hours=True, tz=get_session_timezone()),
            babel=True,
        )
        try:
            index = chart_data['labels'].index(fdate)
            chart_data['values']['posts'][index] += post[1]
            chart_data['values']['threads'][index] += post[2]
            chart_data['values']['replies'][index] += post[3]
            chart_data['values']['mentions'][index] += post[4]
            chart_data['values']['medias'][index] += post[5]
        except:
            pass
    return chart_data


def _get_chart_data_user_word_count(site_id, user_id):
    word_count = AnalyzerPostComment.getMonthWordCountByUser(
        site_id, user_id, limit=300
    )
    chart_data = {
        'words': [],
        'count': [],
    }
    for key in word_count.keys():
        chart_data['words'].append(key)
        chart_data['count'].append(word_count[key])
    return chart_data


@gmg.route('/get_chart_data', methods=['POST'])
def get_chart_data():
    request_data = request.get_json(silent=True)
    name = request_data.get('name', '').lower()
    site_id = request_data.get('site_id', 0)
    if not name or not site_id:
        return jsonify({'error': True, 'errormsg': _('Invalid parameters')})
    errormsg = None
    if name == 'activity_7d':
        data = _get_chart_data_activity_7d(site_id)
    elif name == 'activity_24h':
        data = _get_chart_data_activity_24h(site_id)
    elif name == 'user_activity_7d':
        options = request_data.get('options', {})
        if 'user_id' in options:
            data = _get_chart_data_user_activity_7d(site_id, options['user_id'])
        else:
            errormsg = _('Invalid user!')
    elif name == 'user_word_count':
        options = request_data.get('options', {})
        if 'user_id' in options:
            data = _get_chart_data_user_word_count(site_id, options['user_id'])
        else:
            errormsg = _('Invalid user!')
    else:
        errormsg = _('Invalid Chart!')
    if errormsg:
        return jsonify({'error': True, 'errormsg': errormsg})
    return data


@gmg.route('/csp_report', methods=['POST'])
@csrf.exempt
def csp_report():
    _logger.error('[CSP REPORT] {}'.format(request.data.decode()))
    return make_response('', 204)
