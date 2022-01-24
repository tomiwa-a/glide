from passlib.context import CryptContext

from app.models import Status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password:str):
    return pwd_context.hash(password)

def checkStatus(status:Status):
    if(status == Status.pending): return "pending"
    if(status == Status.active): return "active"
    if(status == Status.disabled): return "disabled"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)