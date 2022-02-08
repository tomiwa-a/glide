from typing import List, Optional
from pydantic import EmailStr, parse_obj_as

from sqlalchemy import cast, func
import sqlalchemy
from .. import models, schema, utils, oauth
from ..database import get_db
from fastapi import FastAPI, Query, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

router = APIRouter(
    prefix = "/withdrawal",
    tags = ['withdrawal']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
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

@router.get("/{id}")
def withdraw(response:Response, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):
    pass