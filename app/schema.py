from enum import Enum
from typing import List, Optional
from dotenv import Any
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

from sqlalchemy.engine import create_engine

from app.database import Base

class Status(str, Enum):
    pending = 'pending'
    active = 'active'
    disabled = 'disabled'

    class Config:
        orm_mode = True
    
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
    status: Status = Status.active

class CreateMerchantStaff(BaseModel):
    name: str
    username: str
    password: str
    first_time: int = 1
    merchant: int
    merchant_branch: int = 0
    role: int
    status: Status = Status.active

class MainProduct(BaseModel):
    name: str

    class Config:
        orm_mode = True

class CreateMainProduct(BaseModel):
    name: str

class ChangeMerchantStatus(BaseModel):
    status: Status

class Merchant(BaseModel):
    id: int
    name: str
    products: List[int]
    logo: Optional[str]
    status: str
    
    created_at: datetime

    class Config:
        use_enum_values = True
        orm_mode = True

# class CreateMerchant(BaseModel):
#     pass