"""add statuses to some tables

Revision ID: 38a5e5d5346c
Revises: f7c82a3ad1ee
Create Date: 2022-01-18 22:12:03.553833

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38a5e5d5346c'
down_revision = 'f7c82a3ad1ee'
branch_labels = None
depends_on = None


def upgrade():
    # op.add_column(table_name="merchant_staff", 
    # column=sa.Column("status", sa.Enum("active", "disabled", "pending", name='myenum', native_enum=True))
    # ) 
    pass


def downgrade():
    # op.drop_column("merchant_staff", "status")
    pass
