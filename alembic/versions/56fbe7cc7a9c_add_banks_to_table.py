"""add banks to table

Revision ID: 56fbe7cc7a9c
Revises: 5620443a90cb
Create Date: 2022-02-03 16:47:55.946599

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, insert
from sqlalchemy import orm


# revision identifiers, used by Alembic.
revision = '56fbe7cc7a9c'
down_revision = '5620443a90cb'
branch_labels = None
depends_on = None


def upgrade():

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    banks = table("banks", 
    column("name", sa.String()),
    column("code", sa.Integer()),
    column("tag", sa.String()),
    )

    bank_insert = [
        {
            "name": "JAIZ BANK",
            "code": 301,
            "tag": "jaiz"
        }, 
        {
            "name": "Parkway",
            "code": 311,
            "tag": "parkway"
        },
        {
            "name": "PAYCOM",
            "code": 305,
            "tag": "paycom"
        },
        {
            "name": "SKYE BANK PLC",
            "code": 76,
            "tag": "skyebank"
        },
        {
            "name": "Stanbic Mobile",
            "code": 304,
            "tag": "stanbic-mobile"
        },
        {
            "name": "Stanbic IBTC Bank Plc",
            "code": 221,
            "tag": "stanbic"
        },
        {
            "name": "Sterling BANK PLC",
            "code": 232,
            "tag": "sterling"
        },
        {
            "name": "UNION BANK OF NIGERIA PLC",
            "code": 32,
            "tag": "unionbank"
        },
        {
            "name": "UNITED BANK FOR AFRICA",
            "code": 33,
            "tag": "uba"
        },
        {
            "name": "UNITY BANK PLC",
            "code": 215,
            "tag": "unity"
        },
        {
            "name": "WEMA BANK PLC",
            "code": 35,
            "tag": "wema"
        },
        {
            "name": "ZENITH BANK PLC",
            "code": 57,
            "tag": "zenith"
        },
        {
            "name": "ZENITH MOBILE",
            "code": 322,
            "tag": "zenith-mobile"
        },
        {
            "name": "KEYSTONE BANK PLC",
            "code": 82,
            "tag": "keystone"
        },
        {
            "name": "HERITAGE BANK",
            "code": 30,
            "tag": "heritage"
        },
        {
            "name": "ACCESS BANK NIGERIA",
            "code": 44,
            "tag": "access"
        },
        {
            "name": "ACCESS MOBILE",
            "code": 323,
            "tag": "access-mobile"
        },
        {
            "name": "AFRIBANK NIGERIA PLC",
            "code": 14,
            "tag": "afribank"
        },
        {
            "name": "DIAMOND BANK PLC",
            "code": 63,
            "tag": "diamond"
        },
        {
            "name": "ECOBANK MOBILE",
            "code": 307,
            "tag": "ecobank-mobile"
        },
        {
            "name": "ECOBANK NIGERIA PLC",
            "code": 50,
            "tag": "ecobank"
        },
        {
            "name": "GTBANK PLC",
            "code": 58,
            "tag": "gtb"
        },
        {
            "name": "GTBANK MOBILE MONEY",
            "code": 315,
            "tag": "gtb-mobile"
        },
        {
            "name": "FIRST CITY MONUMENT BANK",
            "code": 214,
            "tag": "fcmb"
        },
        {
            "name": "FIRST BANK PLC",
            "code": 11,
            "tag": "firstbank"
        },
        {
            "name": "FIDELITY BANK PLC",
            "code": 70,
            "tag": "fidelity"
        },
        {
            "name": "FIRST MOBILE",
            "code": 309,
            "tag": "first-mobile"
        }
    ]

    ret = session.execute(insert(banks).values(bank_insert)) 

def downgrade():
    pass
