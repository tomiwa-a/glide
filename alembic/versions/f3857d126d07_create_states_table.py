"""create states table

Revision ID: f3857d126d07
Revises: 7922166fd3a7
Create Date: 2022-01-19 16:08:11.203835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3857d126d07'
down_revision = '7922166fd3a7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("states", 
    sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
    sa.Column("state", sa.String(), nullable=False),
    sa.Column("country_id", sa.Integer(), sa.ForeignKey("countries.id", ondelete="CASCADE"))
    )


def downgrade():
    op.drop_table("states")
