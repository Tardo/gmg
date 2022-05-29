# GMG Copyright 2022 - Alexandre Díaz
from gmg import gmg
import click
import os
from pathlib import Path
from flask import render_template, current_app
from flask.cli import FlaskGroup, ScriptInfo, with_appcontext
from flask_babel import _
from gmgl.sqlalchemy.database import db
from gmgl.sqlalchemy.models import RecordMetadata
from gmgl.sqlalchemy.models.internal import AppWebConfig
from gmgl.sqlalchemy.xml_loader import load_xml_records


@gmg.cli.command('upgrade')
def upgrade():
    cur_ver = AppWebConfig.get_param('version', '0.0.0')
    next_ver = current_app.config['VERSION']
    if cur_ver > next_ver:
        print(_('Trying a downgrade from {} to {}').format(cur_ver, next_ver))
    elif cur_ver == next_ver:
        print(_("Don't need upgrade... restoring record values!"))
    else:
        print(_('Upgrading from {} to {}...').format(cur_ver, next_ver))
    _finish_install_upgrade()


@gmg.cli.command('install')
def install():
    print(_('Creating tables and records...'))
    db.create_all()
    _finish_install_upgrade()


@gmg.cli.command('install_test')
def install_test():
    print(_('Creating records...'))
    processed_ids = load_xml_records(
        os.path.join(Path(__file__).resolve().parent, 'data', 'records.xml'),
        igroup='base',
    )
    if processed_ids:
        AppWebConfig.set_param('version', current_app.config['VERSION'])
        db.session.commit()


def _finish_install_upgrade():
    processed_ids = load_xml_records(
        os.path.join(Path(__file__).resolve().parent, 'data', 'records.xml'),
        igroup='base',
    )
    if processed_ids:
        _drop_old_records(processed_ids)
        AppWebConfig.set_param('version', current_app.config['VERSION'])
        print(_('Commiting changes...'))
        db.session.commit()
        print(_('All done!'))
    else:
        print(_('Operation cancelled!'))


def _drop_old_records(processed_ids):
    records = RecordMetadata.query.filter(
        RecordMetadata.iref.not_in(processed_ids)
    ).all()
    for record in records:
        record_ref = record.toRecord()
        if record_ref:
            db.session.delete(record_ref)
        else:
            db.session.delete(record)
        print(_('Deleted {} ({})').format(record.object_model, record.iref))
