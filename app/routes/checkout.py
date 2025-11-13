from fastapi import APIRouter, Depends, HTTPException, status, Form
from database import get_db
from sqlalchemy.orm import Session
from .authRouter import get_current_user
from models.orders import Order ,Order_Item
from models.products import Product
from typing import Optional, List
from pydantic import BaseModel, Field
from models.users import User
from models.carts import Cart_Item
from models.coupons import Coupons, Used_coupons
from datetime import datetime
import uuid


class BillItem(BaseModel):
    id: Optional[uuid.UUID]
    quantity: int
    product_id: Optional[uuid.UUID]
    product_name: str
    unit_price: float
    sub_total: float

    class Config:
        from_attributes = True


class CheckOutResponse(BaseModel):
    items: Optional[List[BillItem]]
    total_amount: Optional[float] = 0
    final_amount:Optional[float]=0
    discount_amount: Optional[float] = 0
    coupon_applied: bool = False
    purchase_date:datetime = Field(default_factory=datetime.now)


router = APIRouter(tags=["checkout"])




@router.post("/checkout", response_model=CheckOutResponse)
def checkoutHandler(
    couponCode: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    db:Session=Depends(get_db)
):
    if not user.cart or not user.cart.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart is empty")

    cart_items = (db.query(Cart_Item).filter(Cart_Item.cart_id == user.cart.id).all())
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items in cart")

    bill_items: List[BillItem] = []
    total_amount = 0
    discount_amount = 0

    for crt in cart_items:
        sub_total = crt.quantity * crt.product.unit_price
        total_amount += sub_total
        bill_items.append(
            BillItem(
                id=crt.id,
                quantity=crt.quantity,
                product_id=crt.product_id,
                product_name=crt.product.product_name,
                unit_price=crt.product.unit_price,
                sub_total=sub_total,
            )
        )

    print("coupon :",couponCode)
    if couponCode:
        couponData = db.query(Coupons).filter(Coupons.coupon_code == couponCode).first()
        
        if not couponData:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid coupon code")

        discount_amount = couponData.amount
        final_amount=total_amount-discount_amount 

        if final_amount < 0:
            final_amount=0;

    return CheckOutResponse(
        items=bill_items,
        total_amount=total_amount,
        discount_amount=discount_amount,
        final_amount=final_amount ,
        coupon_applied=bool(couponCode),
    )
