from email.policy import HTTP
from os import stat
from statistics import mode
from typing import List, Optional
from pydantic import parse_obj_as

from sqlalchemy import cast, func
import sqlalchemy
from .. import models, schema, utils, oauth
from ..database import get_db
from fastapi import FastAPI, Query, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import session
from sqlalchemy.orm import Session

router = APIRouter(
    prefix = "/branch",
    tags = ['branch']
)

