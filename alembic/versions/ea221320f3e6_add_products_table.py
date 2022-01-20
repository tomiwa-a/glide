"""add products table

Revision ID: ea221320f3e6
Revises: 38a5e5d5346c
Create Date: 2022-01-18 22:13:03.776064

"""
from enum import auto
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea221320f3e6'
down_revision = '38a5e5d5346c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("products", 
    sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False), 
    sa.Column("branch_id", sa.Integer(), sa.ForeignKey(column="merchant_branches.id", ondelete="CASCADE"), nullable=False), 
    sa.Column("product_id", sa.Integer(), sa.ForeignKey(column="main_products.id", ondelete="CASCADE"), nullable=False),
    sa.Column("price",  sa.Float(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )


def downgrade():
    op.drop_table("products")
