"""create users table

Revision ID: 898ef5ffe0c9
Revises: f3857d126d07
Create Date: 2022-01-19 22:54:29.990690

"""
from time import time
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '898ef5ffe0c9'
down_revision = 'f3857d126d07'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users",
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False, autoincrement=True),
    sa.Column("first_name", sa.String(), nullable=False),
    sa.Column("last_name", sa.String(), nullable=False),
    sa.Column("email", sa.String(), nullable=False, unique=True),
    sa.Column("password", sa.String(), nullable=False),
    sa.Column("phone_number", sa.String(), nullable=False),
    sa.Column("country", sa.Integer(), sa.ForeignKey("countries.id")), 
    sa.Column("state", sa.Integer(), sa.ForeignKey("states.id")),
    sa.Column("referal", sa.Integer(), unique=True, nullable=False),
    sa.Column("dob", sa.Date()), 
    sa.Column("address", sa.String()),
    sa.Column("balance", sa.Float(), default=0),
    sa.Column("pin", sa.Integer()),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text('now()')), 
    sa.Column("status", postgresql.ENUM("active", "disabled", "pending", name='status', create_type=False), nullable=False)
    )


def downgrade():
    op.drop_table("users")
