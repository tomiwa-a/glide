from dis import dis
from email.policy import HTTP
from math import prod
import math
from textwrap import indent
from typing import List, Optional
from pydantic import EmailStr, parse_obj_as
import requests, json

from sqlalchemy import cast, distinct, func
import sqlalchemy
from .. import models, schema, utils, oauth
from ..database import get_db
from fastapi import FastAPI, Query, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..config import settings

router = APIRouter(
    prefix = "/users",
    tags = ['users']
)

#get single user

@router.get("/")
def get_single_user(response:Response, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):

    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    user_ret = db.query(models.Users).filter(models.Users.id == user.id).first()
    return user_ret


#get all users

@router.get("/all")
def get_all_users(response:Response, db:Session = Depends(get_db), user=Depends(oauth.get_current_admin), limit:int =10, skip:int = 0,):
    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    users = db.query(models.Users).order_by(models.Users.id.desc()).limit(limit).offset(skip).all()

    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    
    user_count = db.query(models.Users).count()
    final = {}
    final['status'] = "success"
    final['total'] = user_count
    final['users'] = users

    return final


#check if phone has been used
@router.get("/check_phone/{phone}")
def check_phone(response:Response, phone:str, db:Session = Depends(get_db)):

    check = db.query(models.Users).filter(models.Users.phone_number == phone).first()
    if check:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Phone number has been used")
    
    return {
        "detail": "Phone number has not been used"
    }

#check if email has been used
@router.get("/check_email/{email}")
def check_phone(response:Response, email:EmailStr, db:Session = Depends(get_db)):

    check = db.query(models.Users).filter(models.Users.email == email).first()
    if check:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email has been used")
    
    return {
        "detail": "Email has not been used"
    }


#create a user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.Token)
def create_user(response:Response, payload:schema.CreateUser, db:Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.phone_number == payload.phone_number).first()
    if user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cannot create user with same phone number twice") 
            
    referal =  payload.referal
    payload = payload.dict()
    payload.pop("referal")

    
    payload['password'] = utils.hash_password(payload['password'])
    payload['referal'] = utils.generate_referal(db)

    user = models.Users(**payload)
    db.add(user)
    db.commit()
    db.refresh(user)

    if referal != 0:
        check_ref = db.query(models.Users).filter(models.Users.referal == referal).first()
        if check_ref:
            ref = dict()
            ref['user_id'] = check_ref.id
            ref['refered_id'] = user.id

            ref = models.Referals(**ref)
            db.add(ref)
            db.commit()


    access_token = oauth.create_access_token(data={
        "user_id":user.id
        })
    
    return {
        "status": "success",
        "access_token": access_token
    }

#update a user

#get referals table or something 

@router.get("/referals")
def get_referals(response:Response, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):
    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    ref = db.query(models.Referals).filter(models.Referals.user_id == user.id).count()
    return ref
    
@router.post("/send-money", response_model=schema.ViewSendMoney, status_code=status.HTTP_201_CREATED)
def send_money(response:Response, payload:schema.SendMoney, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):
    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    # check amount + fees is in balance

    if user.balance <= payload.amount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insufficient balance",)

    if user.phone_number == payload.phone_number:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cannot send money to yourself",)

    # check if telepone number exists
    other_user = db.query(models.Users).filter(models.Users.phone_number == payload.phone_number).first()
    if not other_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with phone number {payload.phone_number} doesn't exist")
    # insert send fees into transactions table 
    send_charge:int = 50
    new_amount = payload.amount - send_charge
    
    utils.make_transaction(db, user.id, schema.TransactionStatus.successful, send_charge, schema.TransactionDesc.send_fees, schema.TransactionPos.negative )
    # insert into send money table for history use 

    payload = payload.dict()

    payload['user_id'] = user.id

    send_money = models.SendMoney(**payload)
    db.add(send_money)
    db.commit()
    db.refresh(send_money)
    send_money_id = send_money.id

    # modify both users balances.
    new_user = dict()
    new_user['balance'] = user.balance - payload['amount']
    user_update = db.query(models.Users).filter(models.Users.id == user.id)
    user_update.update(new_user, synchronize_session=False)
    db.commit()

    new_user = dict()
    new_user['balance'] = other_user.balance + new_amount
    user_update = db.query(models.Users).filter(models.Users.id == other_user.id)
    user_update.update(new_user, synchronize_session=False)
    db.commit()

    
    # insert send and receive transaction for sender and receiver respectively
    utils.make_transaction(db, user.id, schema.TransactionStatus.successful, new_amount, schema.TransactionDesc.send, schema.TransactionPos.negative, send_money.id )
    utils.make_transaction(db, other_user.id, schema.TransactionStatus.successful, new_amount, schema.TransactionDesc.receive, schema.TransactionPos.positive, send_money.id )

    # return send money table ? idk yet
    send_money = db.query(models.SendMoney).filter(models.SendMoney.id == send_money_id).first()
    return send_money

@router.post("/deposit", response_model=schema.ViewDeposit, status_code=status.HTTP_201_CREATED)
def send_money(response:Response, payload:schema.Deposit, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):
    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    deposit = db.query(models.Deposit).filter(models.Deposit.reference_id == payload.reference_id).first()
    if deposit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cannot use same reference twice")
    payload = payload.dict()
    payload['user_id'] = user.id

    deposit = models.Deposit(**payload)
    db.add(deposit)
    db.commit()
    db.refresh(deposit)

    deposit_id  = deposit.id
    
    # update amount

    utils.make_transaction(db, user.id, schema.TransactionStatus.successful, payload['amount'], schema.TransactionDesc.deposit, schema.TransactionPos.positive, deposit_id)

    new_user = dict()
    new_user['balance'] = user.balance + payload['amount']
    user_update = db.query(models.Users).filter(models.Users.id == user.id)
    user_update.update(new_user, synchronize_session=False)
    db.commit()

    deposit = db.query(models.Deposit).filter(models.Deposit.id == deposit_id).first()
    return deposit
    
@router.patch("/update_pin")
def update_pin(response:Response, payload:schema.UpdatePin, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):
    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    user_check = db.query(models.Users).filter(models.Users.id == user.id)

    payload = payload.dict()

    user_check.update(payload, synchronize_session=False)
    db.commit()

    return user_check.first()

@router.patch("/update_picture")
def update_picture(response:Response, payload:schema.UpdatePicture, db:Session = Depends(get_db), user=Depends(oauth.get_current_user)):
    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    user_check = db.query(models.Users).filter(models.Users.id == user.id)

    payload = payload.dict()

    user_check.update(payload, synchronize_session=False)
    db.commit()

    return user_check.first()

@router.get("/get_closest")
def get_closest(response:Response, db:Session = Depends(get_db), user=Depends(oauth.get_current_user), longitude:str = "", lattitude:str = "", product:int = 0):

    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    if not (longitude or lattitude or product):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Longitude, Lattitude & Product id are required")

    product_name = db.query(models.MainProducts).filter(models.MainProducts.id == product).first()
    if not product_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not available")
    product_name = vars(product_name)['name']

    # SELECT DISTINCT(a.*) FROM merchant_branches a JOIN products b ON a.id = b.branch_id WHERE a.state = 8 AND a.status = 'active' AND ( b.product_id = 1 AND b.status = 'active')

    # branch = db.query(models.MerchantBranch).filter(models.MerchantBranch.status == models.Status.active).filter(models.MerchantBranch.state == user.state).all()

    branches = db.query(models.MerchantBranch).join(models.Products, models.MerchantBranch.id == models.Products.branch_id).filter(models.MerchantBranch.state == user.state).filter(models.MerchantBranch.status == models.Status.active).filter(models.Products.status == models.Status.active).filter(models.Products.product_id == product).group_by(models.MerchantBranch.id).all()
    
    # print(branch)

    if not branches:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No branches selling close to you.")
    
    destinations = list()
    new_str = ""
    count = 0

    for branch in branches:
        branch = vars(branch)
        # print(branch)
        min_dest = list()
        long = branch['longitude']
        latt = branch['lattitude']

        min_dest = [long, latt]
        
        if count:
            new_str = new_str + "|"

        new_str = new_str + long + ","+latt
        destinations.append(min_dest)
        count = count + 1
    
    # print(destinations)

    # for branch in

    try:

        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?destinations={new_str}&origins={longitude},{lattitude}&key={settings.distance_matrix_api_key}"

        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        json_data = json.loads(response.text)

        data = json_data['rows'][0]['elements']

        distance_dict = dict()

        for i in range(len(data)):
            new_data = data[i]
            if new_data['status'] != "OK":
                continue
            distance_dict[i] = new_data['distance']['value']

        # print(distance_dict)
        # print(data)
        a = sorted(distance_dict.items(), key=lambda x: x[1])
        a = dict((x, y) for x, y in a)
        # print(a[0])

        # generate the list
        gen_list = list()

        for key, value in enumerate(a.items()):
            # print(key, value[1])
            new_branch = vars(branches[key])
            branch_id = new_branch['id']
            check_price = db.query(models.Products).filter(models.Products.branch_id == branch_id).filter(models.Products.product_id == product).first()
            # print(check_price)
            new_branch['status'] = utils.checkStatus(new_branch['status'])
            new_branch['price'] = vars(check_price)['price']
            new_branch['distance'] = value[1]/1000
            new_branch['product_id'] = vars(check_price)['id']

            gen_list.append(new_branch)

        final = dict()

        final['status'] = "successful"
        final['product'] = product_name
        final['merchants'] = gen_list

        # print(json.dumps(json_data['rows'][0]['elements'][1], indent=2))
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error calculating locations")

    return final

@router.get("/purchase_detail")
def get_purchase_detail(response:Response, db:Session = Depends(get_db), user=Depends(oauth.get_current_user), size:float = 0, distance:float = 0,  product_id: int = 0, longitude:str="", lattitude:str ="" ):

    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    if not (longitude or lattitude or product_id or size or distance):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Longitude, Lattitude, size, distance & Product id are required")

    # get the price of the thingy

    product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product doesn't exist")
    
    #get branch_id

    product = vars(product)
    price = product['price']
    branch_id = product['branch_id']
    main_product_id = product ['product_id']

    main_product = db.query(models.MainProducts).filter(models.MainProducts.id == main_product_id).first()
    main_product = vars(main_product)

    branch = db.query(models.MerchantBranch).filter(models.MerchantBranch.id == branch_id).first()
    branch = vars(branch)

    distance_time = 36 #seconds
    distance_seconds = distance * (size * distance_time) 


    estimated_time = distance_seconds / 60
    #3% off per kg, min of 18 naira 

    service = (3/100)* price
    if service < 18:
        service = 18

    service = service * size
    print(service)

    main_price = price * size

    delivery_dist = 40
    if distance < 5:
        delivery_dist = 50
        

    delivery_price = 200 + 100 + (delivery_dist*distance)

    transaction_charge = (1.5/100) * (main_price + delivery_price)

    total_price = main_price + delivery_price + transaction_charge

    finale = dict()
    finale['status'] = "successful"
    final = dict()
    finale['details'] = final
    
    final['product_name'] = main_product['name']

    ##

    merchant_details = dict()
    final['merchant_details'] = merchant_details

    merchant_details['name'] = branch['name']
    merchant_details['longitude'] = branch['longitude']
    merchant_details['lattitude'] = branch['lattitude']
    # merchant_details['address'] = branch['address']

    ##
    final['distance'] = distance
    final['size'] = size
    final['estimated_time'] = str(math.ceil(estimated_time)) + " minutes"
    final['price'] = price
    final['main_price'] = main_price
    final['delivery_price'] = delivery_price
    final['transaction_charge'] = "{:.2f}".format(transaction_charge)
    final['total_price'] = "{:.2f}".format(total_price)
    

    # "10 minutes, 30 seconds"

    return finale
    #get branch details then the branch details.

    # SELECT * FROM merchants a JOIN merchant_branches b ON WHERE a.id = b.merchant AND b.id = branch_id 

    #80 % of delivey goes to driver
    # (the real amount - aggreed commision ) * no of kg

@router.post("/make_purchase")
def make_purchase(response:Response, payload:schema.MakePayment, db:Session = Depends(get_db), user=Depends(oauth.get_current_user), ):

    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    if user.balance < payload.total_amount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insufficient balance",)

    payload = vars(payload)
    payload['user_id'] = user.id
    purchase = models.Order(**payload)
    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    purchase_id = purchase.id

    new_user = dict()
    new_user['balance'] = user.balance - payload['total_amount']
    user_update = db.query(models.Users).filter(models.Users.id == user.id)
    user_update.update(new_user, synchronize_session=False)
    db.commit()

    utils.make_transaction(db, user.id, schema.TransactionStatus.pending, payload['total_amount'], schema.TransactionDesc.purchase, schema.TransactionPos.negative, purchase_id)

    purchase = db.query(models.Order).filter(models.Order.id == purchase_id).first()

    return purchase
