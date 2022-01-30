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
    prefix = "/merchant",
    tags = ['merchant']
)

# view all merchants
@router.get("/")
def get_merchants(response:Response, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin), limit:int =10, skip:int = 0, merchant_status:Optional[schema.Status] = "", q:Optional[str] = ""):
    
    if admin == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    merchants = db.query(models.Merchants)

    if merchant_status:
        merchants = merchants.filter(models.Merchants.status == merchant_status)

    if q:
        q = q.strip(" ")
        search = "%{}%".format(q)
        merchants = merchants.filter(models.Merchants.name.like(search))
        
    merchants = merchants.limit(limit).offset(skip).all()

    if not merchants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No merchants found with parameters")
    
    for merchant in merchants:
        merchant = vars(merchant)
        merchant['status'] = utils.checkStatus(merchant['status'])
    
    final = dict()


    final['filter'] = {
        "show": limit, 
        "skip": skip, 
        "status": merchant_status,
    }

    final['merchants'] = parse_obj_as(List[schema.Merchant], merchants)

    return final


# view a single merchant 

# make the merchant access this too, but just for his umm... , company! 
@router.get("/{id}", response_model=schema.Merchant)
def get_merchants(response:Response, id:int, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):

    if admin == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    merchant = db.query(models.Merchants).filter(models.Merchants.id == id).first()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No merchant with id {id} found")
    merchant = vars(merchant)
    merchant['status'] = utils.checkStatus(merchant['status'])
    return merchant


# create a merchant & merchant staff
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_merchant(response:Response, payload:schema.CreateMerchant, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):

    if admin == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    merchant_details = payload
    merchant = payload.dict()

    check_merchant = db.query(models.Merchants).filter(models.Merchants.name == merchant_details.name.strip(" ")).first()
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
    merchant_staff['name'] = merchant_details.name.strip(" ") + " Merchant"
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

    merchant = db.query(models.Merchants).filter(models.Merchants.name == merchant_details.name).first()
    merchant_staff = db.query(models.MerchantStaff, models.MerchantRoles.name.label("role_name"), func.cast(models.MerchantStaff.status, sqlalchemy.String).label("status")).join(models.MerchantRoles, models.MerchantStaff.role == models.MerchantRoles.id).filter(models.MerchantStaff.merchant == merchant.id).first()
    
    final = dict()

    merchant = vars(merchant)
    merchant['status'] = utils.checkStatus(merchant['status'])

    final['merchant'] = merchant
    
    final['merchant_staff'] = parse_obj_as(schema.ViewMerchantStaff, merchant_staff)

    return final


# update merchant status
@router.patch("/{id}", response_model=schema.Merchant)
def update_merchant(id:int, payload:schema.ChangeMerchantStatus, response:Response, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):

    if admin == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    merchant = db.query(models.Merchants).filter(models.Merchants.id == id)
    merchant_first = merchant.first()

    if not merchant_first:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Merchant with id {id} not found")
    

    merchant.update(payload.dict(), synchronize_session=False)
    db.commit()
    
    merchant = merchant.first()
    merchant = vars(merchant)
    merchant['status'] = utils.checkStatus(merchant['status'])

    return merchant


# see all merchant's staff 
@router.get("/staff/{id}")
def get_merchants_staff(id:int, response:Response, db:Session = Depends(get_db), user=Depends(oauth.get_admin_merchant), limit:int =10, skip:int = 0, staff_status:Optional[schema.Status] = "", branch:Optional[str] = Query(None), q:Optional[str] = "", staff_role:Optional[str] = Query(None)):

    if user['merchant_status'] == "true":
        merchant_id = user['merchant']['MerchantStaff'].id
        if merchant_id != id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You're not authorized to view merchant with id {id}")
        
        merchant_branch = user['merchant']['MerchantStaff'].merchant_branch
        if merchant_branch != 0:
            branch = merchant_branch

        # return user['merchant']

    merchant = db.query(models.Merchants).filter(models.Merchants.id == id).first()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Merchant with id {id} not found")
    
    staffs = db.query(models.MerchantStaff, models.MerchantRoles.name.label("role_name"), func.cast(models.MerchantStaff.status, sqlalchemy.String).label("status")).join(models.MerchantRoles, models.MerchantStaff.role == models.MerchantRoles.id).filter(models.MerchantStaff.merchant == id)

    if staff_status:
        staffs = staffs.filter(models.MerchantStaff.status == staff_status)

    if q:
        q = q.strip(" ")
        search = "%{}%".format(q)
        staffs = staffs.filter(models.MerchantStaff.name.like(search))

    if branch:
        branch = [int(number) for number in branch.split(",")]
        staffs = staffs.filter(models.MerchantStaff.merchant_branch.in_(branch))

    if staff_role:
        staff_role = [int(number) for number in staff_role.split(",")]
        staffs = staffs.filter(models.MerchantStaff.role.in_(staff_role))
    
    staffs = staffs.limit(limit).offset(skip).all()

    if not staffs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No staff found for this parameters")
     
    final = dict()
    final['merchant_id'] = merchant.id
    final['merchant_name'] = merchant.name
    final['created_at'] = merchant.created_at

    merchant = vars(merchant)
    
    final['status'] = utils.checkStatus(merchant['status'])

    final['filter'] = {
        "show": limit, 
        "skip": skip, 
        "status": staff_status, 
        "branch": branch,
        "query" :q,
        "role": staff_role
    }
    
    final['merchant_staff'] = parse_obj_as(List[schema.ViewMerchantStaff], staffs)

    return final


#see all merchant's branch
@router.get("/branch/{id}")
def get_merchants_branch(id:int, response:Response, db:Session = Depends(get_db), user=Depends(oauth.get_admin_merchant), limit:int =10, skip:int = 0, branch_status:Optional[schema.Status] = "", q:Optional[str] = ""):
    merchant = db.query(models.Merchants).filter(models.Merchants.id == id).first()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Merchant with id {id} not found")

    branch = db.query(models.MerchantBranch).all()
    return branch



#disable a branch

#update a branch

#create staff & assign to branch

