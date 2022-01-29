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
    prefix = "/staff",
    tags = ['staff']
)

#get all staffs

#get single staff
@router.get("/{id}")
def get_single_staff():
    pass

#create a staff
@router.post("/merchant", status_code=status.HTTP_201_CREATED, response_model=schema.ViewMerchantStaff)
def create_merchant_staff(response:Response, payload:schema.CreateMerchantStaff, db:Session = Depends(get_db), user=Depends(oauth.get_admin_merchant)):
    
    if user['merchant_status'] == "true":
        merchant_id = user['merchant']['MerchantStaff'].id
        if merchant_id != payload.merchant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You're not authorized to create staff for id {payload.merchant}")
    
    merchant = db.query(models.Merchants).filter(models.Merchants.id == payload.merchant).first()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Merchant with id {payload.merchant} not found")

    check_staff = db.query(models.MerchantStaff).filter(models.MerchantStaff.username == payload.username).first()
    if check_staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username has been taken")

    payload.password = utils.hash_password(payload.password)
    merchant_staff = models.MerchantStaff(**payload.dict())
    db.add(merchant_staff)
    db.commit()
    db.refresh(merchant_staff)
    
    staff_id = merchant_staff.id

    merchant_staff = db.query(models.MerchantStaff, models.MerchantRoles.name.label("role_name"), func.cast(models.MerchantStaff.status, sqlalchemy.String).label("status")).join(models.MerchantRoles, models.MerchantStaff.role == models.MerchantRoles.id).filter(models.MerchantStaff.id == staff_id).first()

    return merchant_staff


#update staff