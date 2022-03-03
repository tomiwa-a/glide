"""create order table

Revision ID: 11f9600518df
Revises: a72cc1177082
Create Date: 2022-03-03 11:08:29.584111

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11f9600518df'
down_revision = 'a72cc1177082'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product', sa.Integer(), nullable=False),
    sa.Column('estimated_time', sa.String(), nullable=False),
    sa.Column('distance', sa.Float(), nullable=False),
    sa.Column('size', sa.Float(), nullable=False),
    sa.Column('longitude', sa.String(), nullable=False),
    sa.Column('lattitude', sa.String(), nullable=False),
    sa.Column('main_amount', sa.Float(), nullable=False),
    sa.Column('delivery_amount', sa.Float(), nullable=False),
    sa.Column('total_amount', sa.Float(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order')
    # ### end Alembic commands ###
