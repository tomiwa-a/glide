"""create merchants table

Revision ID: 40f059c93dfc
Revises: 
Create Date: 2022-01-18 20:57:21.586569

"""
from http import server
from time import time
from tkinter.tix import INTEGER
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40f059c93dfc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("merchants",
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("products", sa.ARRAY(sa.Integer), nullable=True),
    sa.Column("logo", sa.String(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()') ), 
    )


def downgrade():
    op.drop_table("merchants")
