"""create merchant roles table

Revision ID: fed72d123f3f
Revises: ea221320f3e6
Create Date: 2022-01-18 22:54:55.116319

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = 'fed72d123f3f'
down_revision = 'ea221320f3e6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("merchant_roles",
    sa.Column("id", sa.Integer(), nullable=False, primary_key=True, autoincrement=True), 
    sa.Column("name", sa.String(), nullable=False))

    merchant_roles = table("merchant_roles",
    column('name', sa.String())
    )

    op.bulk_insert(merchant_roles, 
    [
        {'name': 'merchant'},
        {'name': 'branch'}, 
        {'name': 'worker'}
    ]
    )


def downgrade():
    op.drop_table("merchant_roles")
