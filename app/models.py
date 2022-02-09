import enum
from multiprocessing.dummy import Array
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Date, Enum, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base

class Status(enum.Enum):
    pending = 1
    active = 2
    disabled = 3

# class TransactionDesc(enum.Enum):
#     withdrawal_fees = 'Withdrawal Fees'
#     withdrawal = 'Withdrawal'
#     deposit = 'Deposit'


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False) 
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    status = Column(Enum(Status), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,  server_default=text('now()'))

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    country = Column(Integer, ForeignKey("countries.id"))
    state = Column(Integer, ForeignKey("states.id"))
    referal = Column(Integer, unique=True, nullable=False)
    dob = Column(Date)
    address = Column(String)
    balance = Column(Float, default=0)
    pin = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    status = Column(Enum(Status), nullable=False)

class MainProducts(Base):
    __tablename__ = "main_products"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class Merchants(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    products = Column(ARRAY(Integer), nullable=True)
    logo = Column(String, nullable=True)
    status = Column(Enum(Status), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()') )

class MerchantBranch(Base):
    __tablename__ = "merchant_branches"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    merchant_id = Column(Integer,  ForeignKey(ondelete="CASCADE", column="merchants.id"), nullable=False)
    country = Column(Integer, ForeignKey("countries.id"))
    state = Column(Integer, ForeignKey("states.id"))
    longitude = Column(String, nullable=True) 
    lattitude = Column( String, nullable=True)
    products = Column(ARRAY(Integer), nullable=False)
    status = Column(Enum(Status), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class MerchantRoles(Base):
    __tablename__ = "merchant_roles"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class MerchantStaff(Base):
    __tablename__ = "merchant_staff"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    role = Column(Integer, ForeignKey(column="merchant_roles.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    first_time = Column(Integer, nullable=False) # 0-> first time, 1 -> last time
    merchant = Column(Integer, ForeignKey(column="merchants.id", ondelete="CASCADE"),  nullable=False)
    merchant_branch = Column(Integer, nullable=False)
    status = Column(Enum(Status), nullable=False)
    created_by= Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # role_name = relationship("MerchantRoles")

class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    branch_id = Column(Integer, ForeignKey(column="merchant_branches.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey(column="main_products.id", ondelete="CASCADE"), nullable=False)
    price = Column(Float, nullable=False)
    status = Column(Enum(Status), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class States(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    state = Column(String, nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))

class Countries(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    country = Column(String , nullable=False)

class Referals(Base):
    __tablename__ = "referals"
    user_id = Column(Integer, ForeignKey(column="users.id", ondelete="CASCADE"), nullable=False, primary_key=True) 
    refered_id = Column(Integer, ForeignKey(column="users.id", ondelete="CASCADE"), nullable=False, primary_key=True)

class Banks(Base):
    __tablename__ = "banks"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(Integer, nullable=False)
    tag = Column(String, nullable=False)

class Withdrawal(Base):
    __tablename__ = "withdrawal"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey(column="users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    account_number = Column(String, nullable=False)
    bank = Column(Integer, ForeignKey(column="banks.id"),  nullable=False)
    status = Column(Enum(Status), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    bank_detail = relationship("Banks")
    user_detail = relationship("Users")

class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey(column="users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    position = Column(String, nullable=False)
    status = Column(String, nullable=False)
    order_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    

# class Post(Base):
#     __tablename__ = "posts"

#     id = Column(Integer, primary_key=True, nullable=False)
#     title = Column(String, nullable=False)
#     content = Column(String, nullable=False)
#     published = Column(Boolean, nullable=False, server_default='TRUE')
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

#     owner = relationship("User")


# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, nullable=False)
#     email = Column(String, nullable=False, unique=True)
#     password = Column(String, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
#     phone_number = Column(Integer, nullable=False, unique=True)

# class Votes(Base):
#     __tablename__ = "votes"

#     post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True, nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)

#     post = relationship("Post")
#     user = relationship("User")

