from enum import Enum
from typing import List, Optional
from dotenv import Any
from pydantic import BaseModel, EmailStr, validator
from datetime import date, datetime

from sqlalchemy.engine import create_engine

from app.database import Base
from app.models import MerchantRoles

class Status(str, Enum):
    pending = 'pending'
    active = 'active'
    disabled = 'disabled'

class Login(BaseModel):
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

class MerchantRole(BaseModel):
    name: str

    class Config:
        orm_mode = True

class MerchantStaff(BaseModel):
    id: int
    name: str
    username: str
    first_time: int
    merchant_branch: int
    # role_name: str
    # status: str
    created_by: datetime

    class Config:
        orm_mode = True

class ViewMerchantStaff(BaseModel):
    MerchantStaff: MerchantStaff
    role_name: str
    status: str

    class Config:
        orm_mode = True

