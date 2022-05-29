import traceback
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
from .models import RecordMetadata, get_db_env
from .database import db


def load_xml_records(xmlpath, igroup=None, commit=True):
    result = []
    try:
        if commit:
            with db.session.begin_nested():
                result = _load_xml_records(xmlpath, igroup)
        else:
            result = _load_xml_records(xmlpath, igroup)
    except Exception as err:
        print(f'Something goes wrong while loading records from xml!')
        print(traceback.format_exc())
    if commit:
        db.session.commit()
    else:
        db.session.flush()
    return result


def _load_xml_records(xmlpath, igroup):
    print(f"Loading xml records from '{xmlpath}'...")
    tree = ET.parse(xmlpath)
    root = tree.getroot()
    db_env = get_db_env()
    record_ids = []
    selector = (
        f".//record[@import_group='{igroup}']"
        if igroup
        else './/record[not(@import_group)]'
    )
    for record in root.findall(selector):
        model_tablename = record.attrib.get('model')
        if not model_tablename:
            raise Exception('No model given!')
        record_id = record.attrib.get('id')
        if not record_id:
            raise Exception('No id for {} given!'.format(model_tablename))
        fields = {}
        for field in record.findall('.//field'):
            name = field.attrib.get('name')
            value_ref = field.attrib.get('ref')
            value_eval = field.attrib.get('eval')
            if value_ref:
                record_obj_ref = RecordMetadata.ref(value_ref)
                if not record_obj_ref:
                    raise Exception("Invalid reference '{}'".format(value_ref))
                value = record_obj_ref.id
            elif value_eval:
                value = eval(
                    value_eval,
                    {
                        'ref': RecordMetadata.ref,
                        'datetime': datetime,
                        'timedelta': timedelta,
                    },
                )
            else:
                value = field.text or field.attrib.get('value')
            fields.update({name: value})
        record_obj = RecordMetadata.ref(record_id)
        if record_obj:
            for field_name in fields:
                setattr(record_obj, field_name, fields[field_name])
            db.session.flush()
            print(f'Updated {model_tablename} ({record_id}): {fields}')
        else:
            record_obj = db_env[model_tablename](**fields)
            db.session.add(record_obj)
            db.session.flush()
            db.session.add(
                RecordMetadata(
                    iref=record_id,
                    object_model=model_tablename,
                    object_id=record_obj.id,
                )
            )
            db.session.flush()
            print(f'Created {model_tablename} ({record_id}): {fields}')
        record_ids.append(record_id)
    return record_ids
