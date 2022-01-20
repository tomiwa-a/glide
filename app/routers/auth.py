from fastapi import FastAPI, APIRouter, Depends, HTTPException, Response, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import mode
from .. import schema, models, utils, oauth
from ..database import get_db

router = APIRouter(
    tags=["auth"]
)

@router.post("/login", response_model=schema.Token)
def login(response:Response, payload:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    # hashed_pwd = utils.hash_password(payload.password)
    # print(hashed_pwd)
    user = db.query(models.User).filter(models.User.email == payload.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Account with email '{payload.username}' not found")

    if not utils.verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Passowrds don't match bozo")
    

    access_token = oauth.create_access_token(data={"user_id":user.id})
    response.status_code = status.HTTP_200_OK
    return {
        "access_token": access_token, 
        "token_type": "Bearer Token"
    }
