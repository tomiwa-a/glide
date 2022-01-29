from typing import List, Optional

from sqlalchemy import func
from .. import models, schema, utils, oauth
from ..database import get_db
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import session
from sqlalchemy.orm import Session

router = APIRouter(
    prefix = "/product",
    tags = ['product']
)

@router.get("/", response_model=List[schema.MainProduct])
def get_products(response:Response, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):
    
    products = db.query(models.MainProducts).all()

    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No main product found")

    return products

@router.get("/{id}", response_model=schema.MainProduct)
def get_products(response:Response, id:int, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):
    
    products = db.query(models.MainProducts).filter(models.MainProducts.id == id).first()

    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with {id} not found")

    return products

@router.post("/")
def get_products(response:Response, payload:schema.CreateMainProduct, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):
    

    products = db.query(models.MainProducts).filter(models.MainProducts.name == payload.name).first()

    if products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product '{payload.name}' exists")

    product = models.MainProducts(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)

    return product