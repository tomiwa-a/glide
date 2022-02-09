from typing import List, Optional
from pydantic import EmailStr, parse_obj_as

from sqlalchemy import cast, func
import sqlalchemy
from .. import models, schema, utils, oauth
from ..database import get_db
from fastapi import FastAPI, Query, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

router = APIRouter(
    prefix = "/transactions",
    tags = ['transaction']
)

@router.get("/transaction_status")
def get_transaction_status():
    enum_list = list(map(lambda c: c.value, schema.TransactionStatus))
    return enum_list

@router.get("/transaction_description")
def get_transaction_description():
    enum_list = list(map(lambda c: c.value, schema.TransactionDesc))
    return enum_list

@router.get("/{id}", response_model=schema.ViewTransaction)
def get_single_transaction(response:Response, id:int, db:Session = Depends(get_db), user=Depends(oauth.get_admin_user)):

    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    transaction = db.query(models.Transactions).filter(models.Transactions.id == id).first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No transaction Found")

    if(user['user_status'] == "true"):
        if transaction.user_id != user['user'].id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized to view transaction", headers={"WWW-Authenticate": "Bearer"})

    return transaction

@router.get("/", response_model=List[schema.ViewTransaction])
def get_all_transactions(response:Response, db:Session = Depends(get_db), user=Depends(oauth.get_admin_user), limit:int =10, skip:int = 0, transaction_status:Optional[schema.TransactionStatus] = "", transaction_description:Optional[schema.TransactionDesc] = ""):

    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    transactions = db.query(models.Transactions)

    if(user['user_status'] == "true"):
        transactions = transactions.filter(models.Transactions.user_id == user['user'].id)

    if transaction_status:
        transactions = transactions.filter(models.Transactions.status == transaction_status)

    if transaction_description:
        transactions = transactions.filter(models.Transactions.description == transaction_description)

    transactions = transactions.limit(limit).offset(skip).all()

    if not transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No transactions")

    return transactions