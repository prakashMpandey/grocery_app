from fastapi import APIRouter,Depends,HTTPException,status,Response,Request,File,UploadFile,Form
from models.wishlist import Wishlist,Wishlist_item
from models.products import Product
from models.carts import Cart,Cart_Item
from database import get_db
from .authRouter import get_current_user
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session,joinedload
from typing import Annotated,Optional
from pydantic import BaseModel,Field
from models.users import User
from sqlalchemy import select
from typing import List
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid


router=APIRouter(tags=["customer"])

class CartInModel(BaseModel):
    product_id:str
    quantity:int=Field(...,ge=1)


class ProductOutModal(BaseModel):
    id:Optional[uuid.UUID]=Field(description="product id")
    product_name:Optional[str]=Field(description="name of the product")
    product_image:Optional[str]=Field(description="product image")
    unit_price:Optional[int]=Field(description="price of single unit")
    pass

class CartItemOutModel(BaseModel):
    id:Optional[uuid.UUID]=Field(description="cart id")
    quantity:Optional[int]=Field(description="quantity")
    product:Optional[ProductOutModal]=Field("product details")

    pass



@router.post("/cart")
def addCartItem(cart_item:CartInModel,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    
    print(cart_item)
    cart=db.query(Cart).filter(Cart.user_id==user.id).first()

    if not cart:
         new_cart = Cart(user_id=user.id)
         db.add(new_cart)
         db.commit()
         db.refresh(new_cart)
         cart = new_cart
        
         pass

    product=db.query(Product).filter(Product.id==cart_item.product_id).first()

    if not product:
        raise HTTPException(status_code=404,detail="product not found")
    
    try:
        new_item=Cart_Item(cart_id=cart.id,product_id=cart_item.product_id,quantity=cart_item.quantity)
        product.popularity+=1
        db.add(new_item)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail="cannot add item to cart")

    return {"status":201,"success":True,"message":"cart item added successfully"}


@router.delete("/cart/{cartItemId}")
def deleteCartItem(cartItemId:str,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    
    cart=db.query(Cart).filter(Cart.user_id==user.id).first()

    if not cart:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="cart is empty")
    
    cartItem=db.query(Cart_Item).filter(Cart_Item.cart_id==cart.id,Cart_Item.id==cartItemId).first()

    if not cartItem:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="cart item not found")
    
    db.delete(cartItem)
    db.commit()

    return {"status":200,"success":True,"message":"cart item deleted successfully"}


@router.get("/cart",response_model=List[CartItemOutModel])
def getCartItems(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    cart=db.query(Cart).filter(Cart.user_id==user.id).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="cart is empty")
    
    cart_items=(db.query(Cart_Item).options(joinedload(Cart_Item.product)).filter(Cart_Item.cart_id==cart.id).all())

    return cart_items

    
    