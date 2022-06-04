"""imp: add web event index

Revision ID: 770b8fc7b0ee
Revises: c5454911444d
Create Date: 2022-06-04 06:21:47.420570

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '770b8fc7b0ee'
down_revision = 'c5454911444d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_analyzer_web_event_origin_post_id'), 'analyzer_web_event', ['origin_post_id'], unique=False)
    op.create_index(op.f('ix_analyzer_web_event_user_id'), 'analyzer_web_event', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_analyzer_web_event_user_id'), table_name='analyzer_web_event')
    op.drop_index(op.f('ix_analyzer_web_event_origin_post_id'), table_name='analyzer_web_event')
