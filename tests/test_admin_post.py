# GMG Copyright 2022 - Alexandre Díaz
import json
from datetime import datetime, timedelta
from flask import session
from gmgl.sqlalchemy.models import RecordMetadata
from gmgl.utils import date_to_str, time_to_str


def _login_admin(client):
    client.post(
        '/login',
        data=dict(username='admin_test', password='pass_test'),
        follow_redirects=True,
    )


def test_refresh_cpu_host(client):
    with client:
        # Public
        response = client.post('/_refresh_cpu_host')
        json_data = response.json
        assert json_data is None
        # Admin
        _login_admin(client)
        response = client.post('/_refresh_cpu_host')
        json_data = response.json
        assert json_data is not None


def test_refresh_uptime_host(client):
    with client:
        # Public
        response = client.post('/_refresh_uptime_host')
        json_data = response.json
        assert json_data is None
        # Admin
        _login_admin(client)
        response = client.post('/_refresh_uptime_host')
        json_data = response.json
        assert 'days' in json_data and 'hours' in json_data and 'minutes' in json_data


def test_refresh_disk_host(client):
    with client:
        # Public
        response = client.post('/_refresh_disk_host')
        json_data = response.json
        assert json_data is None
        # Admin
        _login_admin(client)
        response = client.post('/_refresh_disk_host')
        json_data = response.json
        assert (
            'free' in json_data
            and 'percent' in json_data
            and 'total' in json_data
            and 'used' in json_data
        )


def test_refresh_memory_host(client):
    with client:
        # Public
        response = client.post('/_refresh_memory_host')
        json_data = response.json
        assert json_data is None
        # Admin
        _login_admin(client)
        response = client.post('/_refresh_memory_host')
        json_data = response.json
        assert (
            'percent' in json_data
            and 'percent_cached' in json_data
            and 'total' in json_data
            and 'used' in json_data
        )
