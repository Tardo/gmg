# GMG Copyright 2022 - Alexandre Díaz
import json
from datetime import datetime, timedelta
from flask import session
from gmgl.sqlalchemy.models import RecordMetadata
from gmgl.utils import date_to_str, time_to_str


def test_refresh_host_localtime(client):
    with client:
        response = client.post('/_refresh_host_localtime')
        assert 'localtime' in response.json
        assert 'localzone' in response.json


def test_set_dark_theme(client):
    with client:
        response = client.post(
            '/_set_dark_theme',
            data=json.dumps(dict(enable=True)),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert session['dark_theme']
        response = client.post(
            '/_set_dark_theme',
            data=json.dumps(dict(enable=False)),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert not session['dark_theme']


def test_set_timezone(client):
    with client:
        response = client.post(
            '/_set_timezone',
            data=json.dumps(dict(tzstr='Europe/Berlin')),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert session['timezone'] == 'Europe/Berlin'


def test_chart_data_activity_7d(client, records_loader):
    with client:
        records_loader('test_chart_data')
        site_id = RecordMetadata.ref('base_site_test').id
        response = client.post(
            '/get_chart_data',
            data=json.dumps(dict(site_id=site_id, name='activity_7d')),
            content_type='application/json',
        )
        assert response.status_code == 200
        json_data = response.json
        str_now = date_to_str(
            datetime.utcnow(),
            babel=True,
        )
        assert json_data['labels'][-1] == str_now
        assert json_data['values']['medias'][-1] == 1
        assert json_data['values']['mentions'][-1] == 1
        assert json_data['values']['posts'][-1] == 1
        assert json_data['values']['posts'][-2] == 2
        assert json_data['values']['replies'][-2] == 1
        assert json_data['values']['users'][-1] == 1
        assert json_data['values']['users'][-2] == 2


def test_chart_data_activity_24h(client, records_loader):
    with client:
        records_loader('test_chart_data')
        site_id = RecordMetadata.ref('base_site_test').id
        response = client.post(
            '/get_chart_data',
            data=json.dumps(dict(site_id=site_id, name='activity_24h')),
            content_type='application/json',
        )
        assert response.status_code == 200
        json_data = response.json
        startday = datetime.utcnow().replace(minute=0, second=0)
        str_now = f'{date_to_str(startday, hours=True, babel=True)} - {time_to_str(startday + timedelta(hours=1), babel=True)}'
        assert json_data['labels'][-1] == str_now
        assert json_data['values']['medias'][-1] == 1
        assert json_data['values']['mentions'][-1] == 1
        assert json_data['values']['posts'][0] == 1
        assert json_data['values']['posts'][1] == 1
        assert json_data['values']['posts'][-1] == 1
        assert json_data['values']['replies'][0] == 1
        assert json_data['values']['users'][0] == 1
        assert json_data['values']['users'][1] == 1
        assert json_data['values']['users'][-1] == 1


def test_chart_data_user_activity_7d(client, records_loader):
    with client:
        records_loader('test_chart_data')
        site_id = RecordMetadata.ref('base_site_test').id
        user_id = RecordMetadata.ref('test_user_chart_data_a').id
        response = client.post(
            '/get_chart_data',
            data=json.dumps(
                dict(
                    site_id=site_id,
                    name='user_activity_7d',
                    options={'user_id': user_id},
                )
            ),
            content_type='application/json',
        )
        assert response.status_code == 200
        json_data = response.json
        str_now = date_to_str(
            datetime.utcnow(),
            babel=True,
        )
        assert json_data['labels'][-1] == str_now
        assert json_data['values']['medias'][-1] == 1
        assert json_data['values']['mentions'][-1] == 1
        assert json_data['values']['posts'][-1] == 1
        assert json_data['values']['replies'][-1] == 0
        assert json_data['values']['threads'][-1] == 1


def test_chart_data_user_word_count(client, records_loader):
    with client:
        records_loader('test_chart_data')
        site_id = RecordMetadata.ref('base_site_test').id
        user_id = RecordMetadata.ref('test_user_chart_data_a').id
        response = client.post(
            '/get_chart_data',
            data=json.dumps(
                dict(
                    site_id=site_id,
                    name='user_word_count',
                    options={'user_id': user_id},
                )
            ),
            content_type='application/json',
        )
        assert response.status_code == 200
        json_data = response.json
        assert json_data['count'][0] == 1
        assert 'test' in json_data['words']


def test_csp_report(client):
    with client:
        response = client.post('/csp_report', data=dict(report='The report'))
        assert response.status_code == 204
