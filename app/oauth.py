from jose import JWTError, jwt
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app import schema
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

from .database import get_db
from . import models, schema
from .config import settings

admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl='./admin_login')

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
            raise credentials_exception
        token_data = schema.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    
    return token_data

def get_current_admin(token:str = Depends(admin_oauth2_scheme), db:Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_admin_token(token, credentials_exception)
    admin = db.query(models.Admin).filter(token.id == models.Admin.id).first()
    return admin

def get_current_staff(token:str = Depends(admin_oauth2_scheme), db:Session = Depends(get_db)):
    pass

def get_admin_merchant(admin:str = Depends(get_current_admin), merchant:str = Depends(get_current_staff)):
    if not (admin or merchant):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
        
# def get_current_user(token:str = Depends(oauth2_scheme), db:Session = Depends(get_db)):
#     credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
#     token = verify_access_token(token, credentials_exception)
#     user = db.query(models.User).filter(token.id == models.User.id).first()
#     return user


