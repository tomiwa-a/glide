from enum import Enum
from typing import List, Optional
from dotenv import Any
from pydantic import BaseModel, EmailStr, constr, validator
from datetime import date, datetime

from sqlalchemy.engine import create_engine

from app.database import Base
from app.models import MerchantRoles

class Status(str, Enum):
    pending = 'pending'
    active = 'active'
    disabled = 'disabled'

class Login(BaseModel):
    username: constr(strip_whitespace=True)
    password: constr(strip_whitespace=True)

class UserLogin(BaseModel):
    telephone: constr(strip_whitespace=True)
    password: constr(strip_whitespace=True)

class Token(BaseModel):
    status: str
    access_token: str

    class Config:
        orm_mode = True

class TokenData(BaseModel):
    id: Optional[str] = None

class CreateMerchant(BaseModel):
    name: str
    products: List[int]
    logo:Optional['str']
    status: Status = Status.active

class CreateMerchantStaff(BaseModel):
    name: constr(strip_whitespace=True)
    username: constr(strip_whitespace=True)
    password: constr(strip_whitespace=True)
    first_time: int = 1
    merchant: int
    merchant_branch: int = 0
    role: int
    status: Status = Status.active

class MainProduct(BaseModel):
    name: constr(strip_whitespace=True)

    class Config:
        orm_mode = True

class CreateMainProduct(BaseModel):
    name: constr(strip_whitespace=True)

class ChangeMerchantStatus(BaseModel):
    status: Status

class Merchant(BaseModel):
    id: int
    name: constr(strip_whitespace=True)
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
    name: constr(strip_whitespace=True)

    class Config:
        orm_mode = True

class MerchantStaff(BaseModel):
    id: int
    name: constr(strip_whitespace=True)
    username: constr(strip_whitespace=True)
    first_time: int
    merchant_branch: int
    # role_name: constr(strip_whitespace=True)
    # status: constr(strip_whitespace=True)
    created_by: datetime

    class Config:
        orm_mode = True

class ViewMerchantStaff(BaseModel):
    MerchantStaff: MerchantStaff
    role_name: constr(strip_whitespace=True)
    status: constr(strip_whitespace=True)

    class Config:
        orm_mode = True

class CreateMerchantBranch(BaseModel):
    name:constr(strip_whitespace=True)
    merchant_id: int
    country: int
    state: int
    longitude: Optional[str]
    lattitude: Optional[str]
    products: List[int]
    status: Status = Status.active

class ViewStates(BaseModel):
    id: int
    state: constr(strip_whitespace=True)

    class Config:
        orm_mode = True

class CreateCountry(BaseModel):
    country: constr(strip_whitespace=True)

class CreateState(BaseModel):
    state: constr(strip_whitespace=True)

class ViewAdmin(BaseModel):
    id: int
    name: constr(strip_whitespace=True)
    username: constr(strip_whitespace=True)
    status: constr(strip_whitespace=True)
    created_at: datetime

    class Config:
        orm_mode = True

class CreateAdmin(BaseModel):
    name: constr(strip_whitespace=True)
    username: constr(strip_whitespace=True)
    status: Status = Status.active
    
# 7.426646669537475, 3.910063533386918

class CreateUser(BaseModel):
    first_name: constr(strip_whitespace=True)
    last_name: constr(strip_whitespace=True)
    phone_number: constr(strip_whitespace=True)
    password: constr(strip_whitespace=True)
    country: int
    state: int
    pin: int
    referal: int = 0
    status: Status = Status.active

class SendMoney(BaseModel):
    phone_number: constr(strip_whitespace=True)
    description: constr(strip_whitespace=True)
    amount: int