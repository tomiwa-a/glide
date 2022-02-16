from typing import Optional
from passlib.context import CryptContext

from app.models import Status, Users, Transactions
from app.schema import TransactionDesc, TransactionPos, TransactionStatus

import random, math

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password:str):
    return pwd_context.hash(password)

def checkStatus(status:Status):
    if(status == Status.pending): return "pending"
    if(status == Status.active): return "active"
    if(status == Status.disabled): return "disabled"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def generate_referal(db):
    while True:
        digits = [i for i in range(0, 10)]
        random_str = ""
        for i in range(8):
            index = math.floor(random.random() * 10)
            random_str += str(digits[index])
        
        check_ref = db.query(Users).filter(Users.referal == random_str).first()
        if not check_ref:
            break

    return random_str

def make_transaction(db, user_id:int, status:TransactionStatus, amount:int, description: TransactionDesc, position:TransactionPos, order_id:int = 0):

    # print(locals())

    transaction = dict()
    transaction['user_id'] = user_id
    transaction['amount'] = amount
    transaction['description'] = description
    transaction['position'] = position
    transaction['status'] = status
    transaction['order_id'] = order_id

    transaction = Transactions(**transaction)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction