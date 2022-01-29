"""insert countries and states

Revision ID: ea7e4715659b
Revises: 615a88edfe42
Create Date: 2022-01-27 10:42:54.767877

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, insert
from sqlalchemy import orm


# revision identifiers, used by Alembic.
revision = 'ea7e4715659b'
down_revision = '615a88edfe42'
branch_labels = None
depends_on = None


def upgrade():

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    countries = table("countries", 
    column("country", sa.String()))

    country = {
            "country": "Nigeria"
        }
    
    ret = session.execute(insert(countries).values(country)) 


    # states = table("states", 
    # column("state", sa.String()),
    # column("country_id", sa.Integer()))

    # state = {
    #     "state": "Oyo",
    #     "country_id": 1
    # }

    # ret = session.execute(insert(states).values(state))

def downgrade():
    op.execute("DELETE FROM countries WHERE country = 'Nigeria'")
