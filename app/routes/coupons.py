from fastapi import APIRouter,Depends,HTTPException
from database import get_db
from .authRouter import get_current_user
from pydantic import BaseModel,Field
from models.users import User
from models.coupons import Coupons
from datetime import datetime
import uuid


router=APIRouter()


class CouponReq(BaseModel):
    coupon_code:str
    amount:float
    expiry_date:datetime
    pass


@router.post("/coupon")
def addCoupon(couponData:CouponReq,user:User=Depends(get_current_user),db=Depends(get_db)):
   try: 
    if user.role!='manager':
        raise HTTPException(status_code=401,detail="only manager is authorized")
    
    db.add(Coupons(
        coupon_code=couponData.coupon_code,
        expiry_date=couponData.expiry_date,
        amount=couponData.amount
    ))
    db.commit()

    return {"status":200,"success":"true","message":"coupon added successfully"}
   except Exception as e:
      raise HTTPException(status_code=500,detail=f"{e}")
   
@router.delete("/coupon/{coupon_id}")
def deleteCoupon(coupon_id:str,user:User=Depends(get_current_user),db=Depends(get_db)):
    try: 
     if user.role!='manager':
        raise HTTPException(status_code=401,detail="only manager is authorized")
     
     coupon=db.query(Coupons).filter(Coupons.id==coupon_id).first()

     if not coupon:
        raise HTTPException(status_code=400,detail="no coupon found")
     
     db.delete(coupon)
     db.commit()

     return {"status":200,"success":"true","message":"coupon deleted successfully"}
    except HTTPException as e:
      raise HTTPException(status_code=500,detail="internal server error")
   