from typing import List, Optional
from pydantic import parse_obj_as

from sqlalchemy import cast, func
import sqlalchemy
from .. import models, schema, utils, oauth
from ..database import get_db
from fastapi import FastAPI, Query, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import session
from sqlalchemy.orm import Session

router = APIRouter(
    prefix = "/branch",
    tags = ['branch']
)


#get all branches
@router.get("/")
def get_all_branches():
    pass


#get single branch

#create a branch

@router.post("/", status_code=status.HTTP_201_CREATED,)
def create_branch(response:Response, payload:schema.CreateMerchantBranch, db:Session = Depends(get_db), user=Depends(oauth.get_admin_merchant)):

    if user['merchant_status'] == "true":
        merchant_id = user['merchant']['MerchantStaff'].id
        if merchant_id != payload.merchant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You're not authorized to create branch for merchant with id {payload.merchant_id}")

    if not (payload.longitude or payload.lattitude):
        payload.status = schema.Status.pending
    return payload, user


#update a branch