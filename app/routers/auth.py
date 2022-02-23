from fastapi import FastAPI, APIRouter, Depends, HTTPException, Response, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import mode
from .. import schema, models, utils, oauth
from ..database import get_db

router = APIRouter(
    tags=["auth"]
)

@router.post("/admin_login", response_model=schema.Token)
def admin_login(response:Response, payload:schema.Login, db:Session = Depends(get_db)):
    
    admin = db.query(models.Admin).filter(models.Admin.username == payload.username).filter(models.Admin.status == "active").first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Admin with username '{payload.username}' not found")

    if not utils.verify_password(payload.password, admin.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect password")

    access_token = oauth.create_access_token(data={
        "admin_id":admin.id,
        "role": "admin"
        })
    
    response.status_code = status.HTTP_200_OK
    return {
        "status": "success",
        "access_token": access_token
    }

@router.post("/merchant_login")
def admin_login(response:Response, payload:schema.Login, db:Session = Depends(get_db)):

    merchant = db.query(models.MerchantStaff, models.MerchantRoles).filter(models.MerchantStaff.username == payload.username).filter(models.MerchantStaff.status == "active").join(models.MerchantRoles, models.MerchantStaff.role == models.MerchantRoles.id).first()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Merchant with username '{payload.username}' not found")
    
    if not utils.verify_password(payload.password, merchant.MerchantStaff.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect password")
    
    # return merchant
    access_token = oauth.create_access_token(data={
        "merchant_id":merchant.MerchantStaff.id,
        "role": merchant.MerchantRoles.name
        })
    
    return {
        "status": "success",
        "access_token": access_token
    }

@router.get("/check_logged")
def check_logged(response:Response, db:Session = Depends(get_db), user=Depends(oauth.get_all)):
    return user

@router.post("/user_login", response_model=schema.Token)
def admin_login(response:Response, payload:schema.UserLogin, db:Session = Depends(get_db)):

    user = db.query(models.Users).filter(models.Users.phone_number == payload.telephone).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User not found")

    if not utils.verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect password")

    access_token = oauth.create_access_token(data={
        "user_id":user.id
        })
    
    response.status_code = status.HTTP_200_OK
    return {
        "status": "success",
        "access_token": access_token
    }


# @router.post("/login", response_model=schema.Token)
# def login(response:Response, payload:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
#     # hashed_pwd = utils.hash_password(payload.password)
#     # print(hashed_pwd)
#     user = db.query(models.User).filter(models.User.email == payload.username).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Account with email '{payload.username}' not found")

#     if not utils.verify_password(payload.password, user.password):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Passowrds don't match bozo")
    

#     access_token = oauth.create_access_token(data={"user_id":user.id})
#     response.status_code = status.HTTP_200_OK
#     return {
#         "access_token": access_token, 
#         "token_type": "Bearer Token"
#     }
