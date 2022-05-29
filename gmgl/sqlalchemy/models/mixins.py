# GMG Copyright 2022 - Alexandre Díaz
from sqlalchemy.ext.declarative import declared_attr
from ..database import db


class AnalyzerMixin(object):
    __table_args__ = {'extend_existing': True}

    @declared_attr
    def ref_id(cls):
        """The ID used in the analyzed portal"""
        return db.Column(db.Integer, index=True)

    @declared_attr
    def site_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('site.id', ondelete='CASCADE'),
            nullable=False,
            index=True,
        )

    @declared_attr
    def site(cls):
        return db.relationship('Site', foreign_keys=f'{cls.__name__}.site_id')
