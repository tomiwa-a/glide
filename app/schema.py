from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from sqlalchemy.engine import create_engine

from app.database import Base

