"""changed reference_id to string

Revision ID: 49c5d6bccddb
Revises: 48f0dd8e49e8
Create Date: 2022-02-15 23:34:14.680948

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49c5d6bccddb'
down_revision = '48f0dd8e49e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('deposit', sa.Column('reference', sa.Integer(), nullable=False))
    op.drop_constraint('deposit_reference_id_key', 'deposit', type_='unique')
    op.create_unique_constraint(None, 'deposit', ['reference'])
    op.drop_column('deposit', 'reference_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('deposit', sa.Column('reference_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'deposit', type_='unique')
    op.create_unique_constraint('deposit_reference_id_key', 'deposit', ['reference_id'])
    op.drop_column('deposit', 'reference')
    # ### end Alembic commands ###
