from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from sqlalchemy.engine import create_engine

from app.database import Base


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[float] = None

class UserBase(BaseModel):
    email: EmailStr
    password: str 

class CreatePost(PostBase):
    pass

class CreateUser(UserBase):
    pass

class UpdateUser(BaseModel):
    password: str

class User(BaseModel):
    id: int
    email:EmailStr
    created_at: datetime
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id: Optional[str] = None

class Post(PostBase):
    created_at: datetime
    owner: User
    class Config:
        orm_mode = True

class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True

class Votes(PostBase):
    user: User
    post: Post

    class Config:
        orm_mode = True