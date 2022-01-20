"""create main_products table

Revision ID: 6af0df4e45c0
Revises: 40f059c93dfc
Create Date: 2022-01-18 21:19:45.655221

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = '6af0df4e45c0'
down_revision = '40f059c93dfc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("main_products",
    sa.Column("id", sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
    sa.Column("name", sa.String(), nullable=False)
    )

    main_products = table("main_products",
    column('name', sa.String())
    )

    op.bulk_insert(main_products,
    [
        {'name': 'Gas'},
        {'name': 'Petrol'}
    ]
    )

#     op.bulk_insert(accounts_table,
#     [
#         {'id':1, 'name':'John Smith',
#                 'create_date':date(2010, 10, 5)},
#         {'id':2, 'name':'Ed Williams',
#                 'create_date':date(2007, 5, 27)},
#         {'id':3, 'name':'Wendy Jones',
#                 'create_date':date(2008, 8, 15)},
#     ]
# )


def downgrade():
    op.drop_table("main_products")
