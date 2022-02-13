from typing import List, Optional
from pydantic import EmailStr, parse_obj_as

from sqlalchemy import cast, func
import sqlalchemy
from .. import models, schema, utils, oauth
from ..database import get_db
from fastapi import FastAPI, Query, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
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

#check if phone has been used
@router.get("/check_phone/{phone}")
def check_phone(response:Response, phone:str, db:Session = Depends(get_db)):

    check = db.query(models.Users).filter(models.Users.phone_number == phone).first()
    if check:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Phone number has been used")
    
    return {
        "detail": "Phone number has not been used"
    }

#check if email has been used
@router.get("/check_email/{email}")
def check_phone(response:Response, email:EmailStr, db:Session = Depends(get_db)):

    check = db.query(models.Users).filter(models.Users.email == email).first()
    if check:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email has been used")
    
    return {
        "detail": "Email has not been used"
    }


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

    # check amount + fees is in balance

    if user.balance <= payload.amount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insufficient balance",)

    if user.phone_number == payload.phone_number:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cannot send money to yourself",)

    # check if telepone number exists
    other_user = db.query(models.Users).filter(models.Users.phone_number == payload.phone_number).first()
    if not other_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with phone number {payload.phone_number} doesn't exist")
    # insert send fees into transactions table 
    send_charge:int = 50
    new_amount = payload.amount - send_charge
    
    utils.make_transaction(db, user.id, schema.TransactionStatus.successful, send_charge, schema.TransactionDesc.send_fees, schema.TransactionPos.negative )
    # insert into send money table for history use 

    payload = payload.dict()

    payload['user_id'] = user.id

    send_money = models.SendMoney(**payload)
    db.add(send_money)
    db.commit()
    db.refresh(send_money)
    send_money_id = send_money.id

    # modify both users balances.
    new_user = dict()
    new_user['balance'] = user.balance - payload['amount']
    user_update = db.query(models.Users).filter(models.Users.id == user.id)
    user_update.update(new_user, synchronize_session=False)
    db.commit()

    new_user = dict()
    new_user['balance'] = other_user.balance + new_amount
    user_update = db.query(models.Users).filter(models.Users.id == other_user.id)
    user_update.update(new_user, synchronize_session=False)
    db.commit()

    
    # insert send and receive transaction for sender and receiver respectively
    utils.make_transaction(db, user.id, schema.TransactionStatus.successful, new_amount, schema.TransactionDesc.send, schema.TransactionPos.negative, send_money.id )
    utils.make_transaction(db, other_user.id, schema.TransactionStatus.successful, new_amount, schema.TransactionDesc.receive, schema.TransactionPos.positive, send_money.id )

    # return send money table ? idk yet
    send_money = db.query(models.SendMoney).filter(models.SendMoney.id == send_money_id).first()
    return send_money
