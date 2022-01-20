"""add status to merchants tables

Revision ID: 7879ec0aa663
Revises: c694c38469cc
Create Date: 2022-01-19 14:01:10.928031

"""
from enum import Enum
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '7879ec0aa663'
down_revision = 'c694c38469cc'
branch_labels = None
depends_on = None


def upgrade():
    status = postgresql.ENUM("active", "disabled", "pending", name='status')
    status.create(op.get_bind())

    op.add_column("merchant_staff", column=sa.Column("status", sa.Enum("active", "disabled", "pending", name='status'), nullable=False))
    op.add_column("merchant_branches", column=sa.Column("status", sa.Enum("active", "disabled", "pending", name='status'), nullable=False))
    op.add_column("merchants", column=sa.Column("status", sa.Enum("active", "disabled", "pending", name='status'), nullable=False))
    op.add_column("products", column=sa.Column("status", sa.Enum("active", "disabled", "pending", name='status'), nullable=False))  

def downgrade():
    op.drop_column("merchant_staff", "status")
    op.drop_column("merchant_branches", "status")
    op.drop_column("merchants", "status")
    op.drop_column("products", "status")

    op.execute("DROP TYPE status;")
    
