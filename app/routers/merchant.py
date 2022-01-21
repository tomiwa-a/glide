from email.policy import HTTP
from statistics import mode
from typing import List, Optional

from sqlalchemy import func
from .. import models, schema, utils, oauth
from ..database import get_db
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import session
from sqlalchemy.orm import Session

router = APIRouter(
    prefix = "/merchant",
    tags = ['merchant']
)

@router.get("/")
def get_merchants(response:Response, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):
    
    merchants = db.query(models.Merchants).all()
    return merchants


@router.post("/")
def create_merchant(response:Response, payload:schema.CreateMerchant, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):
    merchant_details = payload
    merchant = payload.dict()

    check_merchant = db.query(models.Merchants).filter(models.Merchants.name == merchant_details.name).first()
    if check_merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant Exists already")

    role = db.query(models.MerchantRoles).filter(models.MerchantRoles.name == "merchant").first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find merchant role in db")

    merchant = models.Merchants(**merchant)
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    

    merchant_staff = {}
    merchant_staff['name'] = merchant_details.name + " Merchant"
    merchant_staff['username'] = "glide_" + merchant_details.name.lower().strip(" ").replace(" ", "_")
    merchant_staff['password'] = utils.hash_password(merchant_staff['username'])
    merchant_staff['merchant'] = merchant.id
    merchant_staff['role'] = role.id
    
    
    try:
        merchant_staff = schema.CreateMerchantStaff(**merchant_staff)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incomplete merchant staff data")
    
    merchant_staff = merchant_staff.dict()
    merchant_staff = models.MerchantStaff(**merchant_staff)
    db.add(merchant_staff)
    db.commit()
    db.refresh(merchant_staff)

    final = db.query()

    return merchant_staff