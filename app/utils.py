from passlib.context import CryptContext

from app.models import Status
from app.models import Users

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
