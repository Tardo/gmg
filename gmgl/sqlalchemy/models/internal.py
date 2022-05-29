# GMG Copyright 2022 - Alexandre Díaz
from typing import Any
from flask import session
from sqlalchemy.exc import NoResultFound
from gmgl.utils import gen_sha256_from_memory
from .base import BaseModel
from ..database import db


class AppWebConfig(BaseModel):
    __tablename__ = 'app_web_config'
    _name_field = 'param'

    param = db.Column(db.String(25), unique=True)
    value_str = db.Column(db.Text)
    value_bool = db.Column(db.Boolean)
    value_int = db.Column(db.Integer)
    value_float = db.Column(db.Float)

    @classmethod
    def get_param(cls, param: str, def_value: Any = None) -> Any:
        try:
            config_param = cls.query.filter_by(param=param).first()
        except NoResultFound as err:
            config_param = None
        if config_param is None:
            return def_value
        elif config_param.value_str is not None:
            return config_param.value_str
        elif config_param.value_bool is not None:
            return config_param.value_bool
        elif config_param.value_int is not None:
            return config_param.value_int
        elif config_param.value_float is not None:
            return config_param.value_float
        return def_value

    @classmethod
    def set_param(cls, param: str, value: Any):
        config_param = cls.query.filter_by(param=param).first()
        if not config_param:
            config_param = cls(param=param)
            db.session.add(config_param)
        if isinstance(value, str):
            config_param.value_str = value
        elif isinstance(value, bool):
            config_param.value_bool = value
        elif isinstance(value, int):
            config_param.value_int = value
        elif isinstance(value, float):
            config_param.value_float = value
        db.session.commit()


class Site(BaseModel):
    __tablename__ = 'site'

    ref = db.Column(db.String(64))
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    post_per_page = db.Column(db.Integer, nullable=True)

    @classmethod
    def get_session_active_site(cls):
        active_site_id = session.get('site_id')
        if active_site_id:
            active_site = cls.query.get(active_site_id)
        else:
            active_site = cls.query.first()
        return active_site


class Attachment(BaseModel):
    __tablename__ = 'attachment'
    _name_field = 'hash_ref'

    def _default_hash_ref(context):
        return gen_sha256_from_memory(context.get_current_parameters()['data'])

    data = db.Column(db.LargeBinary, nullable=False)
    hash_ref = db.Column(
        db.String(64),
        default=_default_hash_ref,
        onupdate=_default_hash_ref,
        unique=True,
        nullable=False,
    )
    mimetype = db.Column(db.String(32), nullable=False)
