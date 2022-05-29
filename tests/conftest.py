# GMG Copyright 2022 - Alexandre Díaz
import pytest
import os
from pathlib import Path
from flask import session
from gmg import create_app
from gmgl.sqlalchemy.xml_loader import load_xml_records
from gmgl.sqlalchemy.database import db
from gmgl.sqlalchemy.models import RecordMetadata
from gmgl.configs import GMGConfigTest


@pytest.fixture()
def records_loader():
    def _load_records(igroup):
        load_xml_records(
            os.path.join(Path(__file__).resolve().parent, 'data/records.xml'),
            igroup=igroup,
            commit=False,
        )

    return _load_records


@pytest.fixture()
def app(records_loader):
    app = create_app(GMGConfigTest())
    with app.app_context():
        db.session.begin_nested()
        records_loader('base')
        yield app
        db.session.rollback()


@pytest.fixture()
def client(app):
    test_client = app.test_client()
    with test_client.session_transaction() as session:
        session['site_id'] = RecordMetadata.ref('base_site_test').id
    return test_client


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
