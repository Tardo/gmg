# GMG Copyright 2022 - Alexandre Díaz
import hashlib
import time
import distro
import subprocess
import os
import base64
from io import BytesIO
from urllib.request import urlopen
from urllib.error import URLError
from functools import wraps
from zoneinfo import ZoneInfo
from pytz import country_timezones
from datetime import datetime
from typing import List
from lxml import etree
from urllib.parse import urlparse
from cssselect import HTMLTranslator, SelectorError
from flask import current_app, session, flash, request, abort
from flask_babel import _, format_date, format_datetime


#################################
# HTML/XML
#################################
def etree_to_string(element, eformat='utf-8'):
    return etree.tostring(element, encoding=eformat).decode(eformat)


def css_xpath(element, css_selector):
    """Helper function to get lxml elements using css selectors"""
    try:
        expression = HTMLTranslator().css_to_xpath(css_selector)
    except SelectorError:
        return []
    return element.xpath(expression)


#################################
# SESSION
#################################
def get_session_timezone():
    try:
        session_tz = session.get('timezone')
        if session_tz:
            tzstr = session_tz
        else:
            tzstr = country_timezones[
                request.accept_languages.best_match(
                    current_app.config['SUPPORT_LANGUAGES']
                )
            ][0]
    except Exception or RuntimeError:
        return current_app.config['DEFAULT_TIMEZONE']
    else:
        return tzstr


def is_session_expired():
    if 'logged_in' in session and session.get('last_activity') is not None:
        now = int(time.time())
        limit = now - 60 * current_app.config['SESSION_TIME']
        last_activity = session.get('last_activity')
        if last_activity < limit:
            return True
        session['last_activity'] = now
    return False


def get_session_login_tries():
    return int(session.get('login_try')) if 'login_try' in session else 0


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(
                _("Error in the '{0}' field - {1}").format(
                    getattr(form, field).label.text, error
                ),
                'danger',
            )


#################################
# DATES
#################################
GMG_DATABASE_DATE_FORMAT = 'YYYY-MM-DD'
GMG_DATABASE_TIME_FORMAT = 'HH:MM:SS'
GMG_DATABASE_DATETIME_FORMAT = f'{GMG_DATABASE_DATE_FORMAT} {GMG_DATABASE_TIME_FORMAT}'
GMG_DATE_FORMAT = '%Y-%m-%d'
GMG_TIME_FORMAT = '%H:%M:%S'
GMG_DATETIME_FORMAT = f'{GMG_DATE_FORMAT} {GMG_TIME_FORMAT}'


def localize_datetime(value, tz=None):
    tz = ZoneInfo(tz or get_session_timezone())
    return value.astimezone(tz)


def str_db_to_date(value, hours=False, tz='UTC'):
    return datetime.strptime(
        value, GMG_DATETIME_FORMAT if hours else GMG_DATE_FORMAT
    ).replace(tzinfo=ZoneInfo(tz))


def int_to_date(value, tz='UTC'):
    return datetime.fromtimestamp(value, tz=ZoneInfo(tz))


def date_to_str(value, hours=False, babel=False):
    if babel:
        if hours:
            return format_datetime(value, 'short')
        else:
            return format_date(value, 'short')
    return value.strftime(GMG_DATETIME_FORMAT if hours else GMG_DATE_FORMAT)


def time_to_str(value, babel=False):
    if babel:
        return format_datetime(value, 'short').split(' ')[1]
    return value.strftime(GMG_TIME_FORMAT)


#################################
# SYSTEM
#################################
def get_public_ip():
    try:
        IP = urlopen('http://api.ipify.org').read().decode('utf-8')
    except URLError:
        IP = None
    return IP


PUBLIC_IP = get_public_ip()


def host_memory_usage():
    """
    returns a dict of host memory usage values
                    {'percent': int((used/total)*100),
                    'percent_cached':int((cached/total)*100),
                    'used': int(used/1024),
                    'total': int(total/1024)}
    """

    out = open('/proc/meminfo')
    for line in out:
        if 'MemTotal:' == line.split()[0]:
            split = line.split()
            total = float(split[1])
        if 'MemFree:' == line.split()[0]:
            split = line.split()
            free = float(split[1])
        if 'Buffers:' == line.split()[0]:
            split = line.split()
            buffers = float(split[1])
        if 'Cached:' == line.split()[0]:
            split = line.split()
            cached = float(split[1])
    out.close()
    used = total - (free + buffers + cached)
    return {
        'percent': int((used / total) * 100),
        'percent_cached': int(((cached) / total) * 100),
        'used': int(used / 1024),
        'total': int(total / 1024),
    }


def host_cpu_percent():
    """
    returns CPU usage in percent
    """

    f = open('/proc/stat', 'r')
    line = f.readlines()[0]
    data = line.split()
    previdle = float(data[4])
    prevtotal = float(data[1]) + float(data[2]) + float(data[3]) + float(data[4])
    f.close()
    time.sleep(0.1)
    f = open('/proc/stat', 'r')
    line = f.readlines()[0]
    data = line.split()
    idle = float(data[4])
    total = float(data[1]) + float(data[2]) + float(data[3]) + float(data[4])
    f.close()
    intervaltotal = total - prevtotal
    percent = 100 * (intervaltotal - (idle - previdle)) / intervaltotal
    return str('%.1f' % percent)


def host_disk_usage(partition=None):
    """
    returns a dict of disk usage values
                    {'total': usage[1],
                    'used': usage[2],
                    'free': usage[3],
                    'percent': usage[4]}
    """

    if not partition:
        partition = '/'

    usage = (
        subprocess.check_output(
            ['df -h %s' % partition], universal_newlines=True, shell=True
        )
        .split('\n')[1]
        .split()
    )
    return {'total': usage[1], 'used': usage[2], 'free': usage[3], 'percent': usage[4]}


def host_localtime():
    cmdr = (
        subprocess.check_output(
            ['date +"%H:%M %Z"'], universal_newlines=True, shell=True
        )
        .split('\n')[0]
        .split(' ')
    )
    return {'localtime': cmdr[0], 'localzone': cmdr[1]}


def host_uptime():
    """
    returns a dict of the system uptime
            {'day': days,
            'time': '%d:%02d' % (hours,minutes)}
    """

    with open('/proc/uptime') as f:
        line = f.readlines()[0]
    uptime = int(line.split(' ')[0].split('.')[0])
    minutes = int(uptime / 60 % 60)
    hours = int(uptime / 60 / 60 % 24)
    days = int(uptime / 60 / 60 / 24)
    return {
        'days': days,
        'hours': hours,
        'minutes': minutes,
    }


def get_linux_distribution():
    return '%s %s' % (distro.name(), distro.version())


def bin2b64(value):
    return value if value is None else base64.b64encode(value).decode('utf-8')


def b642bin(value):
    return value if value is None else BytesIO(base64.b64decode(value))


#################################
# HELPERS
#################################
SHA_BLOCKSIZE = 65536


def is_allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']
    )


def get_url_filename_format(url):
    if not url:
        return ''
    return urlparse(url).path.split('/')[-1].split('.')[-1]


def gen_sha256_from_memory(data):
    if not data:
        return ''
    stream_data = BytesIO(data)
    hasher = hashlib.sha256()
    while len(buf := stream_data.read(SHA_BLOCKSIZE)) > 0:
        hasher.update(buf)
    return hasher.hexdigest()


def gen_sha256_from_string(data):
    if not data:
        return ''
    return gen_sha256_from_memory(data.encode('utf-8'))


def get_supported_languages():
    langs = list()
    for r in os.listdir('%s/translations' % os.getcwd()):
        fullpath = '%s/translations/%s' % (os.getcwd(), r)
        if os.path.isdir(fullpath):
            langs.append(r)
    return langs


#################################
# DECORATORS
#################################
def check_referrer():
    """
    check_referrer validate that the referrer location is in the allowed list
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            can_call = False
            if request.referrer:
                if current_app.config['ALLOWED_ORIGINS'][0] == '*':
                    can_call = True
                else:
                    try:
                        url_parts = urlparse(request.referrer)
                    except:
                        abort(403)
                    fullnetloc = f'{url_parts.scheme}://{url_parts.netloc}'
                    if fullnetloc in current_app.config['ALLOWED_ORIGINS']:
                        can_call = True
            else:
                can_call = True
            if can_call:
                return func(*args, **kwargs)
            abort(403)

        return wrapper

    return decorator


def check_session(level: str):
    """
    check_session validate that the active session has a logged user with the selected level.
    The levels can be:
    - 'user': Only can access registered users
    - 'admin': Only can access superuser
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'logged_in' not in session or not session['logged_in']:
                abort(403)
            elif level.lower() == 'admin' and not session['is_admin']:
                abort(403)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator
