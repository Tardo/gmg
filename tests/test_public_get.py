# GMG Copyright 2022 - Alexandre Díaz
from flask import session
from gmgl.sqlalchemy.models import RecordMetadata


def test_login_logout_admin(client):
    with client:
        client.post(
            '/login',
            data=dict(username='admin_test', password='pass_test'),
            follow_redirects=True,
        )
        assert session['is_admin'] is True
        client.get('/logout')
        assert 'is_admin' not in session


def test_overview(client):
    with client:
        response = client.get('/')
        assert response.status_code == 200


def test_reports(client):
    with client:
        response = client.get('/reports')
        assert response.status_code == 200


def test_multimedia(client):
    with client:
        response = client.get('/multimedia')
        assert response.status_code == 200


def test_users(client):
    with client:
        response = client.get('/users')
        assert response.status_code == 200


def test_user_page(client, records_loader):
    with client:
        records_loader('test_user_page')
        response = client.get('/users/TestUser')
        assert response.status_code == 200
        assert b'Activity last 7 days' in response.data
        response = client.get('/users/test_user_unknown')
        assert response.status_code == 200
        assert b'This user does not exist' in response.data


def test_search(client, records_loader):
    with client:
        records_loader('test_search')
        response = client.get('/search?term=TestUserSearch')
        assert response.status_code == 200
        print(response.text)
        assert b'Activity last 7 days' in response.data
        response = client.get('/search?term=TestUser')
        assert response.status_code == 200
        assert b'Users (1)' in response.data
        assert b'Threads' not in response.data
        response = client.get('/search?term=Test')
        assert response.status_code == 200
        assert b'Users (1)' in response.data
        assert b'Threads (1)' in response.data
        response = client.get('/search?term=TestUserSearchUnknown')
        assert response.status_code == 200
        assert b'No results' in response.data


def test_bin_avatar(client, records_loader):
    with client:
        records_loader('test_bin_avatar')
        response = client.get('/bin/avatar/lazy')
        assert response.status_code == 302
        assert response.headers['Location'] == '/static/img/default_avatar_low.png'
        response = client.get('/bin/avatar/0')
        assert response.status_code == 302
        assert response.headers['Location'] == '/static/img/default_avatar.png'
        attachment_obj = RecordMetadata.ref('test_attachment_bin_avatar_a')
        response = client.get(f'/bin/avatar/{attachment_obj.hash_ref}')
        assert response.status_code == 200
        assert b'This is an avatar test' in response.data
