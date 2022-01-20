"""create merchant staff table

Revision ID: c694c38469cc
Revises: fed72d123f3f
Create Date: 2022-01-18 23:04:25.776816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c694c38469cc'
down_revision = 'fed72d123f3f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("merchant_staff", 
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False, autoincrement=True),
    sa.Column("role", sa.Integer(), sa.ForeignKey(column="merchant_roles.id", ondelete="CASCADE"), nullable=False),
    sa.Column("name", sa.String(), nullable=True), 
    sa.Column("username", sa.String(), nullable=False), 
    sa.Column("password", sa.String(), nullable=False), 
    sa.Column("first_time", sa.Integer(), nullable=False),  # 0-> first time, 1 -> last time
    sa.Column("merchant", sa.Integer(), sa.ForeignKey(column="merchants.id", ondelete="CASCADE"),  nullable=False),
    sa.Column("merchant_branch", sa.Integer(), sa.ForeignKey(column="merchant_branches.id", ondelete="CASCADE")), 
    sa.Column("created_by", sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )


def downgrade():
    op.drop_table("merchant_staff");
