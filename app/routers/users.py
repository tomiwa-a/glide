from typing import List, Optional
from pydantic import parse_obj_as

from sqlalchemy import cast, func
import sqlalchemy
from .. import models, schema, utils, oauth
from ..database import get_db
from fastapi import FastAPI, Query, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import session
from sqlalchemy.orm import Session

import uuid

router = APIRouter(
    prefix = "/users",
    tags = ['users']
)

#get single user

@router.get("/")
def get_single_user(response:Response, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):

    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    user_ret = db.query(models.Users).filter(models.Users.id == user.id).first()
    return user_ret


#get all users

#create a user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.Token)
def create_user(response:Response, payload:schema.CreateUser, db:Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.phone_number == payload.phone_number).first()
    if user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cannot create user with same phone number twice") 
            
    referal =  payload.referal
    payload = payload.dict()
    payload.pop("referal")

    
    payload['password'] = utils.hash_password(payload['password'])
    payload['referal'] = utils.generate_referal(db)

    user = models.Users(**payload)
    db.add(user)
    db.commit()
    db.refresh(user)

    if referal != 0:
        check_ref = db.query(models.Users).filter(models.Users.referal == referal).first()
        if check_ref:
            ref = dict()
            ref['user_id'] = check_ref.id
            ref['refered_id'] = user.id

            ref = models.Referals(**ref)
            db.add(ref)
            db.commit()


    access_token = oauth.create_access_token(data={
        "user_id":user.id
        })
    
    response.status_code = status.HTTP_200_OK
    return {
        "status": "success",
        "access_token": access_token
    }

#update a user

#get referals table or something 

@router.get("/referals")
def get_referals(response:Response, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):
    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    ref = db.query(models.Referals).filter(models.Referals.user_id == user.id).count()
    return ref
    
@router.post("/send-money")
def send_money(response:Response, payload:schema.SendMoney, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):
    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    pass