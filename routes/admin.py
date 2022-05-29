# GMG Copyright 2022 - Alexandre Díaz
from gmg import gmg
from flask import current_app, g, jsonify, request, render_template, session
from flask_csp.csp import csp_header
from gmgl.utils import (
    check_session,
    host_cpu_percent,
    host_uptime,
    host_disk_usage,
    host_memory_usage,
    PUBLIC_IP,
)
from gmgl.nlp.spacy import spacy_nlp
import logging

_logger = logging.getLogger(__name__)


#################################
# GET
#################################
@gmg.route('/nlp_demo', methods=['GET'])
@csp_header()
@check_session(level='admin')
def nlp_demo():
    g.canonical_url = '/nlp_demo'
    session['prev_url'] = request.path
    site_id = session.get('site_id')
    from gmgl.forms import NLPDemoForm

    nlp_demo_form = NLPDemoForm(request.args)
    input_data = request.args.get('input_data', '')
    if nlp_demo_form.validate():
        spacy_nlp.analyze_text(input_data)
    return render_template('pages/nlp_demo.html.j2', nlp_demo_form=nlp_demo_form)


#################################
# POST
#################################
@gmg.route('/_refresh_cpu_host', methods=['POST'])
@check_session(level='admin')
def refresh_cpu_host():
    return jsonify(host_cpu_percent())


@gmg.route('/_refresh_uptime_host', methods=['POST'])
@check_session(level='admin')
def refresh_uptime_host():
    return jsonify(host_uptime())


@gmg.route('/_refresh_disk_host', methods=['POST'])
@check_session(level='admin')
def refresh_disk_host():
    return jsonify(host_disk_usage(partition=current_app.config['PARTITION']))


@gmg.route('/_refresh_memory_host', methods=['POST'])
@check_session(level='admin')
def refresh_memory_containers():
    return jsonify(host_memory_usage())
