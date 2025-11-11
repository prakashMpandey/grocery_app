from fastapi import APIRouter, Depends, HTTPException, status, Form
from database import get_db
from .authRouter import get_current_user
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
    total_amount: float = 0
    discount_amount: float = 0
    coupon_applied: bool = False
    purchase_date: datetime = Field(default_factory=datetime.utcnow)


router = APIRouter(tags=["checkout"])


@router.post("/checkout", response_model=CheckOutResponse)
def checkoutHandler(
    couponCode: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    if not user.cart or not user.cart.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart is empty")

    cart_items = db.query(Cart_Item).filter(Cart_Item.cart_id == user.cart.id).all()
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

    if couponCode:
        couponData = db.query(Coupons).filter(Coupons.coupon_code == couponCode).first()
        if not couponData:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid coupon code")

        isCouponUsedByUser = (
            db.query(Used_coupons)
            .filter(Used_coupons.user_id == user.id, Used_coupons.coupon_id == couponData.id)
            .first()
        )

        if isCouponUsedByUser:
            raise HTTPException(status_code=400, detail="Coupon already used by this user")

        db.add(Used_coupons(user_id=user.id, coupon_id=couponData.id))
        db.commit()

        discount_amount = couponData.amount
        total_amount = max(total_amount - discount_amount, 0)

    return CheckOutResponse(
        items=bill_items,
        total_amount=total_amount,
        discount_amount=discount_amount,
        coupon_applied=bool(couponCode),
    )
