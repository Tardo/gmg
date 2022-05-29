"""Use BLOB

Revision ID: 5d9ab6cd8638
Revises: e072cefe0463
Create Date: 2022-04-24 07:05:57.394829

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5d9ab6cd8638'
down_revision = 'e072cefe0463'
branch_labels = None
depends_on = None


def upgrade():
    return


def downgrade():
    return
