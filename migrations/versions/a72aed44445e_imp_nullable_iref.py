"""imp: nullable iref

Revision ID: a72aed44445e
Revises: a4ac5c97faa6
Create Date: 2022-04-30 08:57:26.307288

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a72aed44445e'
down_revision = 'a4ac5c97faa6'
branch_labels = None
depends_on = None


def _remove_default_iref(session, tablename):
    session.execute(f"update {tablename} set iref = NULL where iref like 'model_%'")


def upgrade():
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'analyzer_post', 'iref', existing_type=sa.VARCHAR(length=92), nullable=True
    )
    op.alter_column(
        'analyzer_post_comment',
        'iref',
        existing_type=sa.VARCHAR(length=92),
        nullable=True,
    )
    op.alter_column(
        'analyzer_post_media',
        'iref',
        existing_type=sa.VARCHAR(length=92),
        nullable=True,
    )
    op.alter_column(
        'analyzer_post_stat', 'iref', existing_type=sa.VARCHAR(length=92), nullable=True
    )
    op.alter_column(
        'analyzer_thread', 'iref', existing_type=sa.VARCHAR(length=92), nullable=True
    )
    op.alter_column(
        'analyzer_thread_category',
        'iref',
        existing_type=sa.VARCHAR(length=92),
        nullable=True,
    )
    op.alter_column(
        'analyzer_user', 'iref', existing_type=sa.VARCHAR(length=92), nullable=True
    )
    op.alter_column(
        'analyzer_web_event', 'iref', existing_type=sa.VARCHAR(length=92), nullable=True
    )
    op.alter_column(
        'app_web_config', 'iref', existing_type=sa.VARCHAR(length=92), nullable=True
    )
    op.alter_column(
        'attachment', 'iref', existing_type=sa.VARCHAR(length=92), nullable=True
    )
    op.alter_column(
        'media_type', 'iref', existing_type=sa.VARCHAR(length=92), nullable=True
    )
    op.alter_column('site', 'iref', existing_type=sa.VARCHAR(length=92), nullable=True)
    op.alter_column(
        'web_event_type', 'iref', existing_type=sa.VARCHAR(length=92), nullable=True
    )
    _remove_default_iref(session, 'analyzer_post')
    _remove_default_iref(session, 'analyzer_post_comment')
    _remove_default_iref(session, 'analyzer_post_media')
    _remove_default_iref(session, 'analyzer_post_stat')
    _remove_default_iref(session, 'analyzer_thread')
    _remove_default_iref(session, 'analyzer_thread_category')
    _remove_default_iref(session, 'analyzer_user')
    _remove_default_iref(session, 'analyzer_web_event')
    _remove_default_iref(session, 'app_web_config')
    _remove_default_iref(session, 'attachment')
    _remove_default_iref(session, 'media_type')
    _remove_default_iref(session, 'site')
    _remove_default_iref(session, 'web_event_type')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'web_event_type', 'iref', existing_type=sa.VARCHAR(length=92), nullable=False
    )
    op.alter_column('site', 'iref', existing_type=sa.VARCHAR(length=92), nullable=False)
    op.alter_column(
        'media_type', 'iref', existing_type=sa.VARCHAR(length=92), nullable=False
    )
    op.alter_column(
        'attachment', 'iref', existing_type=sa.VARCHAR(length=92), nullable=False
    )
    op.alter_column(
        'app_web_config', 'iref', existing_type=sa.VARCHAR(length=92), nullable=False
    )
    op.alter_column(
        'analyzer_web_event',
        'iref',
        existing_type=sa.VARCHAR(length=92),
        nullable=False,
    )
    op.alter_column(
        'analyzer_user', 'iref', existing_type=sa.VARCHAR(length=92), nullable=False
    )
    op.alter_column(
        'analyzer_thread_category',
        'iref',
        existing_type=sa.VARCHAR(length=92),
        nullable=False,
    )
    op.alter_column(
        'analyzer_thread', 'iref', existing_type=sa.VARCHAR(length=92), nullable=False
    )
    op.alter_column(
        'analyzer_post_stat',
        'iref',
        existing_type=sa.VARCHAR(length=92),
        nullable=False,
    )
    op.alter_column(
        'analyzer_post_media',
        'iref',
        existing_type=sa.VARCHAR(length=92),
        nullable=False,
    )
    op.alter_column(
        'analyzer_post_comment',
        'iref',
        existing_type=sa.VARCHAR(length=92),
        nullable=False,
    )
    op.alter_column(
        'analyzer_post', 'iref', existing_type=sa.VARCHAR(length=92), nullable=False
    )
    # ### end Alembic commands ###
