from typing import List, Optional
from pydantic import parse_obj_as

from sqlalchemy import cast, func
import sqlalchemy
from .. import models, schema, utils, oauth
from ..database import get_db
from fastapi import FastAPI, Query, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import session
from sqlalchemy.orm import Session
import requests, json
from ..config import settings

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

    if admin == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

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

    if admin == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

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

@router.post("/states/{id}", status_code=status.HTTP_201_CREATED)
def create_state(response:Response, payload:schema.CreateState, id:int, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):

    if admin == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

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
def update_state(response:Response, payload:schema.CreateState, id:int, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):

    if admin == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

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

    if admin == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

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

    if admin == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

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

@router.patch("/admin")
def change_password(response:Response, payload:schema.ChangeAdminPassword, db:Session = Depends(get_db), admin=Depends(oauth.get_current_admin)):

    if admin == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    admin = db.query(models.Admin).filter(models.Admin.id == admin.id)

    if not admin.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Admin not fouund")

    payload = payload.dict()
    payload['password'] = utils.hash_password(payload['password'])
    admin.update(payload, synchronize_session=False)
    db.commit()
    admin = admin.first()
    return admin

# @router.get("/list_banks")
# def get_banks():
#     url = "https://api.paystack.co/bank?country=nigeria&perPage=100"

#     payload={}
#     headers = {}

#     response = requests.request("GET", url, headers=headers, data=payload)
#     return response.json()

@router.get("/list_banks", response_model=List[schema.ViewBanks])
def get_banks(response:Response, db:Session = Depends(get_db)):
    banks = db.query(models.Banks).all()
    if not banks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No banks found")
    
    return banks

@router.get("/list_banks/{id}", response_model=schema.ViewBanks)
def get_single_bank(response:Response, id:int, db:Session = Depends(get_db)):
    bank = db.query(models.Banks).filter(models.Banks.id == id).first()
    if not bank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No bank found with id {id} found")
    
    return bank

@router.get("/users/send-money/{id}", response_model=schema.ViewSendMoney)
def get_send_money(response:Response, id:int, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):

    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    send_money = db.query(models.SendMoney).filter(models.SendMoney.id == id).first()
    
    if not send_money:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find money trail")

    return send_money

@router.get("/users/deposit/{id}", response_model=schema.ViewDeposit)
def get_single_deposit(response:Response, id:int, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):

    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    deposit = db.query(models.Deposit).filter(models.Deposit.id == id).first()
    
    if not deposit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find deposit")

    return deposit


@router.get("/address_to_coords")
def get_address_to_coords(response:Response, address:str):

    try:

        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={settings.distance_matrix_api_key}"

        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        json_data = json.loads(response.text)
        print(response.text)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error calculating locations")
    final = dict()
    final['address'] = address
    final['location'] = json_data['results'][0]['geometry']['location']
    return final