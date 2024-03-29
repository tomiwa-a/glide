from fastapi import FastAPI
from . import models
from .database import engine
from .routers import auth, merchant, main_product, branch, staff, misc, users, product, withdrawal, transactions
from .config import settings

from fastapi.middleware.cors import CORSMiddleware


# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(merchant.router)
app.include_router(main_product.router)
app.include_router(branch.router)
app.include_router(staff.router)
app.include_router(misc.router)
app.include_router(users.router)
app.include_router(product.router)
app.include_router(withdrawal.router)
app.include_router(transactions.router)

@app.get("/")
def root():
    return{"message": "Welcome to Glide"}
