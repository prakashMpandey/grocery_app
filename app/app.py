from fastapi import FastAPI
from fastapi.responses import JSONResponse
from models import *
from database import Base,engine,session
from pwdlib import PasswordHash
from routes import authRouter
from routes import productRouter
from routes import wishlistRouter
from routes import cartRouter
from routes import salesReport
from routes import checkout
from routes import coupons
from routes import categoryRouter



app=FastAPI()




@app.get("/", summary="Health check", tags=["root"])
def home():
    return JSONResponse(content={"message": "Hello, your API is live!"})


password_hash=PasswordHash.recommended()

Base.metadata.create_all(bind=engine)

app.include_router(authRouter.router)
app.include_router(productRouter.router)
app.include_router(wishlistRouter.router)
app.include_router(cartRouter.router)
app.include_router(checkout.router)
app.include_router(salesReport.router)
app.include_router(coupons.router)
app.include_router(categoryRouter.router)
