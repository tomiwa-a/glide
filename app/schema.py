from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from sqlalchemy.engine import create_engine

from app.database import Base

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminToken(BaseModel):
    status: str
    access_token: str

    class Config:
        orm_mode = True

class TokenData(BaseModel):
    id: Optional[str] = None

class CreateMerchant(BaseModel):
    name: str
    products: List[int]
    status: str = 'active'

class CreateMerchantStaff(BaseModel):
    name: str
    username: str
    password: str
    first_time: int = 1
    merchant: int
    merchant_branch: int = 0
    role: int
    status: str = 'active'

class MainProduct(BaseModel):
    name: str

    class Config:
        orm_mode = True

class CreateMainProduct(BaseModel):
    name: str