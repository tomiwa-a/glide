"""create countries table

Revision ID: 7922166fd3a7
Revises: 7879ec0aa663
Create Date: 2022-01-19 14:20:09.617374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7922166fd3a7'
down_revision = '7879ec0aa663'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("countries", 
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False, autoincrement=True),
    sa.Column("country", sa.String (), nullable=False)
    )


def downgrade():
    op.drop_table("countries")
