from heapq import merge
from jose import JWTError, jwt
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app import schema
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

from .database import get_db
from . import models, schema
from .config import settings

admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/admin_login')

#SECRET KEY
#ALGORITHM  HS256
#EXPIRATION TIME OF THE TOKEN

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data:dict):
    to_encode = data.copy()

    # expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_admin_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id: str = payload.get("admin_id")
        if not id:
            return None
        token_data = schema.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    
    return token_data

def verify_merchant_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id: str = payload.get("merchant_id")
        if not id:
            return None
        token_data = schema.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    
    return token_data

def verify_user_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id: str = payload.get("user_id")
        if not id:
            return None
        token_data = schema.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    
    return token_data

## called by routers

def get_current_admin(token:str = Depends(admin_oauth2_scheme), db:Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_admin_token(token, credentials_exception)
    if token != None:
        admin = db.query(models.Admin).filter(token.id == models.Admin.id).first()
        return admin
    return None
    # if not (admin or token):
    #     return None
    # return admin

def get_current_staff(token:str = Depends(admin_oauth2_scheme), db:Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_merchant_token(token, credentials_exception)
    if token != None:
        merchant =  db.query(models.MerchantStaff, models.MerchantRoles).join(models.MerchantRoles, models.MerchantStaff.role == models.MerchantRoles.id).filter(models.MerchantStaff.status == "active").filter(models.MerchantStaff.id == token.id).first()
        return merchant
    return None

def get_current_user(token:str = Depends(admin_oauth2_scheme), db:Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_user_token(token, credentials_exception)
    if token != None:
        user = db.query(models.Users).filter(token.id == models.Users.id).first()
        return user
    return None

def get_admin_merchant(admin:str = Depends(get_current_admin), merchant:str = Depends(get_current_staff)):
    
    if not (admin or merchant):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    admin_status, merchant_status = "false", "false"
    if admin:
        admin_status = "true"

    if merchant:
        merchant_status = "true"

    return {
        "admin_status": admin_status,
        "merchant_status": merchant_status,
        "admin": admin, 
        "merchant": merchant
    }
    
def get_admin_user(admin:str = Depends(get_current_admin), user:str = Depends(get_current_user)):
    if not (admin or user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    admin_status, user_status = "false", "false"
    if admin:
        admin_status = "true"

    if user:
        user_status = "true"

    return {
        "admin_status": admin_status,
        "user_status": user_status,
        "admin": admin, 
        "user": user
    }

def get_all(admin:str = Depends(get_current_admin), merchant:str = Depends(get_current_staff), user:str = Depends(get_current_user)):

    if not (admin or merchant or user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    admin_status, merchant_status, user_status = "false", "false", "false"
    if admin:
        admin_status = "true"

    if user:
        user_status = "true"

    if merchant:
        merchant_status = "true"

    return {
        "admin_status": admin_status,
        "merchant_status": merchant_status,
        "user_status": user_status,
        "admin": admin, 
        "merchant": merchant,
        "user": user
    }

# def get_current_user(token:str = Depends(oauth2_scheme), db:Session = Depends(get_db)):
#     credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
#     token = verify_access_token(token, credentials_exception)
#     user = db.query(models.User).filter(token.id == models.User.id).first()
#     return user


