# GMG Copyright 2022 - Alexandre Díaz
from gmg import gmg
from flask import make_response, render_template, session
import logging

_logger = logging.getLogger(__name__)


PUBLIC_SESSION_KEYS = (
    'site_id',
    'logged_in',
    'username',
    'uid',
    'prev_url',
    'timezone',
    'is_admin',
    'dark_theme',
)


@gmg.route('/static/js/_dynamic/base.js', methods=['GET'])
def js_dynamic_base():
    session_filtered = {k: v for k, v in session.items() if k in PUBLIC_SESSION_KEYS}
    file_content = render_template(
        'scripts/base.js.j2', session_filtered=session_filtered
    )
    response = make_response(file_content)
    response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
    return response
