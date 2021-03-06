"""fix: web_event avatar change

Revision ID: 8e878081ba47
Revises: 50f03b109fef
Create Date: 2022-04-29 22:13:44.071461

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8e878081ba47'
down_revision = '50f03b109fef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'analyzer_web_event',
        'old_avatar_id',
        type_=sa.Integer,
        postgresql_using='old_avatar_id::integer',
    )
    op.alter_column(
        'analyzer_web_event',
        'new_avatar_id',
        type_=sa.Integer,
        postgresql_using='new_avatar_id::integer',
    )
    op.create_foreign_key(
        None, 'analyzer_web_event', 'attachment', ['old_avatar_id'], ['id']
    )
    op.create_foreign_key(
        None, 'analyzer_web_event', 'attachment', ['new_avatar_id'], ['id']
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'analyzer_web_event', type_='foreignkey')
    op.drop_constraint(None, 'analyzer_web_event', type_='foreignkey')
    # ### end Alembic commands ###
