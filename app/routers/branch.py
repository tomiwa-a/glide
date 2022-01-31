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

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_branch(response:Response, payload:schema.CreateMerchantBranch, db:Session = Depends(get_db), user=Depends(oauth.get_admin_merchant)):

    if user['merchant_status'] == "true":
        merchant_id = user['merchant']['MerchantStaff'].id
        if merchant_id != payload.merchant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You're not authorized to create branch for merchant with id {payload.merchant_id}")

    branch = db.query(models.MerchantBranch).filter(models.MerchantBranch.name == payload.name).first()
    if branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot use the same branch name twice")

    if not (payload.longitude or payload.lattitude):
        payload.status = schema.Status.pending
    
    branch = models.MerchantBranch(**payload.dict())
    db.add(branch)
    db.commit()
    db.refresh(branch)

    role = db.query(models.MerchantRoles).filter(models.MerchantRoles.name == "branch").first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find merchant role in db")

    merchant_staff = {}
    merchant_staff['name'] = branch.name.strip(" ") + " Merchant"
    merchant_staff['username'] = "glide_" + branch.name.lower().strip(" ").replace(" ", "_")
    merchant_staff['password'] = utils.hash_password(merchant_staff['username'])
    merchant_staff['merchant'] = payload.merchant_id
    merchant_staff['merchant_branch'] = branch.id
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

    merchant_staff = db.query(models.MerchantStaff, models.MerchantRoles.name.label("role_name"), func.cast(models.MerchantStaff.status, sqlalchemy.String).label("status")).join(models.MerchantRoles, models.MerchantStaff.role == models.MerchantRoles.id).filter(models.MerchantStaff.merchant_branch == branch.id).first()

    final = dict()

    final['branch'] = branch
    
    final['merchant_staff'] = parse_obj_as(schema.ViewMerchantStaff, merchant_staff)

    return final


#update a branch