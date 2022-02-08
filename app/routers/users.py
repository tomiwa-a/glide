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
    pass

@router.post("/withdraw")
def withdraw(response:Response, payload:schema.Withdraw, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):
    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    if user.balance <= payload.amount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insufficient balance",)

    transfer_charge:int = 100
    
    utils.make_transaction(db, user.id, schema.TransactionStatus.successful, transfer_charge, schema.TransactionDesc.withdrawal_fees, schema.TransactionPos.negative )

    payload = payload.dict()
    main_amount = payload['amount']
    payload['amount'] = int(payload['amount']) - int(transfer_charge)
    payload['user_id'] = user.id

    withdrawal = models.Withdrawal(**payload)
    db.add(withdrawal)
    db.commit()
    db.refresh(withdrawal)

    withdrawal_id = withdrawal.id

    utils.make_transaction(db, user.id, schema.TransactionStatus.pending, payload['amount'], schema.TransactionDesc.withdrawal, schema.TransactionPos.negative, withdrawal_id)

    new_user = dict()
    new_user['balance'] = user.balance - main_amount

    user = db.query(models.Users).filter(models.Users.id == user.id)

    user.update(new_user, synchronize_session=False)
    db.commit()
    
    withdrawal = db.query(models.Withdrawal).filter(models.Withdrawal.id == withdrawal_id).first()

    return withdrawal
    # takes tranfer charge, then withdraws . should make an util for the transfer charge.
    