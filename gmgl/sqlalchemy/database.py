# GMG Copyright 2022 - Alexandre Díaz
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import literal_column
from sqlalchemy.ext import compiler
from sqlalchemy.schema import DDLElement
from flask_sqlalchemy_caching import CachingQuery

# db = SQLAlchemy(session_options={"autoflush": False})
db = SQLAlchemy(None, query_class=CachingQuery)


####################################
# HELPERS
####################################
def db_get_active_user():
    return db.session.bind.url.username


def db_get_engine_name():
    return db.session.bind.name


####################################
# MATERIALIZED VIEWS
# Code by Jeff Widman (http://www.jeffwidman.com/blog/847/using-sqlalchemy-to-create-and-manage-postgresql-materialized-views/)
####################################
class CreateMaterializedView(DDLElement):
    def __init__(self, name, selectable):
        self.name = name
        self.selectable = selectable


@compiler.compiles(CreateMaterializedView)
def db_compile_mt(element, compiler, **kw):
    # Could use "CREATE OR REPLACE MATERIALIZED VIEW..."
    # but I'd rather have noisy errors
    return 'CREATE MATERIALIZED VIEW %s AS %s' % (
        element.name,
        compiler.sql_compiler.process(element.selectable, literal_binds=True),
    )


def db_create_mt(name, selectable, metadata=db.metadata):
    _mt = db.MetaData()  # temp metadata just for initial Table object creation
    t = db.Table(name, _mt)  # the actual mat view class is bound to db.metadata
    for c in selectable.c:
        t.append_column(db.Column(c.name, c.type, primary_key=c.primary_key))
    db.event.listen(metadata, 'after_create', CreateMaterializedView(name, selectable))
    db.event.listen(
        metadata, 'before_drop', db.DDL('DROP MATERIALIZED VIEW IF EXISTS ' + name)
    )
    return t


def db_refresh_mat_view(name, concurrently):
    # since session.execute() bypasses autoflush, must manually flush in order
    # to include newly-created/modified objects in the refresh
    db.session.flush()
    _con = 'CONCURRENTLY ' if concurrently else ''
    db.session.execute('REFRESH MATERIALIZED VIEW ' + _con + name)
