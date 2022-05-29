# GMG Copyright 2022 - Alexandre Díaz
from gmgl.addons import cache
from flask_sqlalchemy_caching import FromCache
from sqlalchemy import event
from flask_babel import _
from . import base
from . import internal
from . import analyzer
from . import mixins
from ..database import db


def get_db_env():
    return {
        c.__tablename__: c
        for c in base.BaseModel.__subclasses__()
        if hasattr(c, '__tablename__')
    }


class RecordMetadata(base.BaseModel):
    __tablename__ = 'record_metadata'
    _name_field = 'iref'

    iref = db.Column(db.String(92), nullable=False, unique=True)
    object_id = db.Column(db.Integer, nullable=False)
    object_model = db.Column(db.String(64), nullable=False)

    db.UniqueConstraint('object_model', 'object_id')

    @classmethod
    def getModel(cls, object_model):
        env = get_db_env()
        model_class = env[object_model]
        if not model_class:
            raise Exception(_('Unknown {} model!').format(object_model))
        return model_class

    @classmethod
    def getRecord(cls, object_model, object_id):
        env = get_db_env()
        model_class = env[object_model]
        record = model_class.query.options(FromCache(cache)).get(object_id)
        return record

    @classmethod
    def ref(cls, iref):
        record = cls.query.options(FromCache(cache)).filter_by(iref=iref).first()
        return record.toRecord() if record else None

    def toRecord(self):
        return self.getRecord(self.object_model, self.object_id)


#################################
# DB MODEL EVENTS
#################################


@event.listens_for(base.BaseModel, 'after_delete', propagate=True)
def base_after_delete(mapper, connection, target):
    @event.listens_for(db.session, 'after_flush', once=True)
    def receive_after_flush(session, context):
        # Delete the RecordMetada associated with the deleted record
        record = RecordMetadata.query.filter_by(
            object_model=target.__tablename__, object_id=target.id
        ).first()
        if record:
            db.session.delete(record)
