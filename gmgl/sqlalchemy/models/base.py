# GMG Copyright 2022 - Alexandre Díaz
from gmgl.addons import cache
from flask_sqlalchemy_caching import FromCache
from sqlalchemy import func
from ..database import db


class BaseModel(db.Model):
    __abstract__ = True

    _name_field = None
    _protected_fields = []

    id = db.Column(db.Integer(), primary_key=True)
    create_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    write_date = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def exists(self):
        primary_key_colnames = self.__table__.primary_key.columns.values()
        values = {
            column.name: getattr(self, column.name) for column in primary_key_colnames
        }
        return self.query.options(FromCache(cache)).filter_by(**values).count() > 0

    def __repr__(self):
        display_name = (
            getattr(self, self._name_field) if self._name_field else '-Unnamed-'
        )
        return '<%r %r>' % (self.__class__.__name__, display_name)
