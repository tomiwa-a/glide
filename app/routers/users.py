from typing import List
from .. import models, schema, utils
from ..database import get_db
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import session
from pydantic import EmailStr

router = APIRouter(
    prefix="/users",
    tags = ['users']
)

@router.get("/", response_model=List[schema.User])
def get_users(db: session = Depends(get_db)):
    users = db.query(models.User).all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
    return users

@router.get("/{email}", response_model=schema.User)
def get_user(email:EmailStr, db: session = Depends(get_db)):
    post = db.query(models.User).filter(models.User.email==email).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return post



@router.post("/", response_model=schema.User)
def create_user(payload:schema.CreateUser, response:Response, db:session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email)
    if  user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cannot add same email twice")
    
    #hash the password
    payload.password = utils.hash_password(payload.password)

    user = models.User(**payload.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    response.status_code = status.HTTP_201_CREATED
    return user

@router.delete("/{email}")
def delete_user(email:EmailStr, db:session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{email}", response_model=schema.User)
def update_user(email:EmailStr, payload:schema.UpdateUser, response:Response, db:session = Depends(get_db)):
    post = db.query(models.User).filter(models.User.email == email)
    check_pwd = post.first()
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    post.update(payload.dict(), synchronize_session=False)
    db.commit()
    response.status_code = status.HTTP_200_OK
    return post.first()