"""Initial migration.

Revision ID: 9fa02b066d0d
Revises:
Create Date: 2022-04-07 23:26:11.506513

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9fa02b066d0d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    return


def downgrade():
    return
