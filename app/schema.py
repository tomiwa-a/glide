from enum import Enum, IntEnum
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

class TransactionDesc(str, Enum):
    withdrawal_fees = 'Withdrawal Fees'
    withdrawal = 'Withdrawal'
    deposit = 'Deposit'
    send_fees = 'Send Fees'
    send = 'Send'
    receive = 'Receive'
    purchase = 'Purchase'

class TransactionPos(str, Enum):
    positive = "positive"
    negative = "negative"

class TransactionStatus(str, Enum):
    pending = 'pending'
    successful = 'successful'
    declined = 'declined'
    cancelled = 'cancelled'

class OrderStatus(str, Enum):
    order_pending = 'Order Pending'
    driver_arrived = 'Driver Arrived'
    order_picked = 'Order Picked'
    order_completed = 'Order Completed'
    order_enroute = 'Order Enroute'
    order_arrived = 'Order Arrived'
    order_confirmed = 'Order Confirmed'
    order_declined = 'Order Declined'

class TransactionFees(IntEnum):
    transfer_charge:int = 100


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
    id: int
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
    created_at: datetime

    class Config:
        orm_mode = True

class CreateAdmin(BaseModel):
    name: constr(strip_whitespace=True)
    username: constr(strip_whitespace=True)
    status: Status = Status.active
    
class ChangeAdminPassword(BaseModel):
    password: constr(strip_whitespace=True)

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

class ViewSendMoney(BaseModel):
    id: int
    phone_number: str
    amount: int
    description: str
    created_at: datetime

    class Config:
        orm_mode = True

class Deposit(BaseModel):
    amount:int
    reference_id: str

class ViewDeposit(BaseModel):
    id: int
    user_id: int
    amount: int
    reference_id: str
    created_at: datetime

    class Config:
        orm_mode = True

class Withdraw(BaseModel):

    amount: int
    account_number: constr(strip_whitespace=True)
    bank: int
    status: Status = Status.pending 

    @validator('amount')
    def check_amount(cls, v):
        if v < 5000:
            raise ValueError("Cannot withdraw less than 5000.")
        return int(v)
        # assert v < 5000, 'Cannot withdraw less than 5000.'

class ViewBanks(BaseModel):
    id: int
    name: str
    code: int
    tag: str

    class Config:
        orm_mode = True

class ViewUser(BaseModel):
    id: int 
    first_name: str
    last_name: str
    country: int
    referal: str
    address: Optional[str]
    pin: int
    email: Optional[str]
    phone_number: str
    state: int
    dob: Optional[date]
    balance: int
    created_at: datetime

    class Config:
        orm_mode = True

class ViewWithdrawals(BaseModel):
    id: int
    amount: int
    bank:int
    account_number: str
    status: str
    created_at: datetime
    

    class Config:
        orm_mode = True

class ViewTransaction(BaseModel):
    id: int
    user_id: int
    amount: int
    description: TransactionDesc
    order_id: int
    position: TransactionPos
    status: TransactionStatus
    created_at: datetime

    class Config:
        orm_mode = True

class UpdatePin(BaseModel):
    pin: int

class UpdatePicture(BaseModel):
    profile_picture: str


class ViewMerchantBranch(BaseModel):
    id: int
    name: str
    products:List[int]
    merchant_id: int
    longitude: str
    lattitude: str
    country: int
    state:int

    class Config:
        orm_mode = True


class MakePayment(BaseModel):
    longitude: str
    lattitude: str
    distance: float
    size: float
    estimated_time: str
    product: int
    main_amount: float
    delivery_amount: float
    total_amount: float
    status: str = OrderStatus.order_pending