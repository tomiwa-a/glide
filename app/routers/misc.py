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
    tags=['misc']
)

# response:Response, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin),

@router.get("/countries")
def get_countires(response:Response, db:Session = Depends(get_db)):
    countries = db.query(models.Countries).all()
    if not countries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No countries found")
    return {
        "status": "success",
        "countries": countries
    }

@router.get("/countries/{id}")
def get_single_country(response:Response, id:int, db:Session = Depends(get_db)):
    country  = db.query(models.Countries).filter(models.Countries.id == id).first()

    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No country with id {id} found")

    states = db.query(models.States).filter(models.States.country_id == id).all()
    return {
        "status": "success",
        "country": country,
        "states" : parse_obj_as(List[schema.ViewStates], states)
    }

@router.post("/countries", status_code=status.HTTP_201_CREATED)
def create_country(response:Response, payload:schema.CreateCountry, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):

    payload.country = payload.country.strip(" ")

    country = db.query(models.Countries).filter(models.Countries.country == payload.country).first()

    if country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cannot add same country twice")

    country = models.Countries(**payload.dict())
    db.add(country)
    db.commit()
    db.refresh(country)
    return country

@router.put("/countries/{id}")
def update_country(response:Response, id:int, payload:schema.CreateCountry, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):

    country = db.query(models.Countries).filter(models.Countries.id == id)
    country_check = country.first()

    if not country_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id {id} not found")

    payload.country = payload.country.strip(" ")
    country_check = db.query(models.Countries).filter(models.Countries.country == payload.country).first()

    if country_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cannot add same country twice")

    country.update(payload.dict(), synchronize_session=False)
    db.commit()
    country = country.first()
    return country
    

@router.get("/states/{id}")
def get_single_state(response:Response, id:int, db:Session = Depends(get_db)):
    state  = db.query(models.States).filter(models.States.id == id).first()

    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No state with id {id} found")
    return {
        "status": "success",
        "state": state,
    }

@router.post("/states/{id}")
def create_state(response:Response, payload:schema.CreateState, id:int, db:Session = Depends(get_db)):
    country  = db.query(models.Countries).filter(models.Countries.id == id).first()

    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No country with id {id} found")
    
    state = db.query(models.States).filter(models.States.state == payload.state).first()
    if state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot add the same state twice")
    
    state = payload.dict()
    state['country_id'] = id

    state = models.States(**state)
    db.add(state)
    db.commit()
    db.refresh(state)
    return state
    

@router.put("/states/{id}")
def update_state(response:Response, payload:schema.CreateState, id:int, db:Session = Depends(get_db)):

    state  = db.query(models.States).filter(models.States.id == id)
    state_check = state.first()

    if not state_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No state with id {id} found")

    state_check = db.query(models.States).filter(models.States.state == payload.state).first()
    if state_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot add same state twice")
    
    state.update(payload.dict(), synchronize_session=False)
    db.commit()
    state = state.first()
    return state

# delete state & delete country. 

#get all admins. 
@router.get("/admin")
def view_admins(response:Response, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin), admin_status:Optional[schema.Status] = "",):

    admins = db.query(models.Admin)
    
    if admin_status:
        admins = admins.filter(models.Admin.status == admin_status)

    admins = admins.all()
    if not admins:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No admins found")

    for admin in admins:
        admin = vars(admin)
        admin['status'] = utils.checkStatus(admin['status'])

    return admins

#create an admin
@router.post("/admin", status_code=status.HTTP_201_CREATED, response_model=schema.ViewAdmin)
def create_admin(response:Response, payload:schema.CreateAdmin, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):

    admin = db.query(models.Admin).filter(models.Admin.username == payload.username).first()

    if admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot create admin with username {payload.username}")

    admin = payload.dict()
    admin['password'] = utils.hash_password(admin['username'])

    admin = models.Admin(**admin)
    db.add(admin)
    db.commit()
    db.refresh(admin)

    

    return admin
