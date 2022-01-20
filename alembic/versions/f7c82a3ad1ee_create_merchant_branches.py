"""create company branches

Revision ID: f7c82a3ad1ee
Revises: 6af0df4e45c0
Create Date: 2022-01-18 21:54:28.977219

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7c82a3ad1ee'
down_revision = '6af0df4e45c0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("merchant_branches",
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False, autoincrement=True), 
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("merchant_id", sa.Integer(),  sa.ForeignKey(ondelete="CASCADE", column="merchants.id"), nullable=False),
    sa.Column("longitude", sa.String(), nullable=False), 
    sa.Column("lattitude", sa.String(), nullable=False),
    sa.Column("products", sa.ARRAY(sa.Integer), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )


def downgrade():
    op.drop_table("merchant_branches")
