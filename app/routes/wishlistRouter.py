from fastapi import APIRouter,Depends,HTTPException,status
from models.wishlist import Wishlist,Wishlist_item
from models.products import Product
from database import get_db
from .authRouter import get_current_user
from sqlalchemy.orm import Session,joinedload
from typing import Optional
from pydantic import BaseModel,Field
from models.users import User
from typing import List
from datetime import datetime
import uuid


router=APIRouter(tags=['wishlist'])

class Wishlist_Model(BaseModel):
    name:str=Field(min_length=3,description="name of the wishlist")

class WishlistItemModel(BaseModel):
    product_id:str


class ProductOut(BaseModel):
    id:Optional[uuid.UUID]=Field(description="product id")
    product_name:Optional[str]=Field(description="product name")
    unit_price:Optional[float]
    product_image:Optional[str]

    class Config:
        from_attributes=True

class WishlistItemOut(BaseModel):
    id:Optional[uuid.UUID]
    wishlist_id:Optional[uuid.UUID]
    created_at:Optional[datetime]
    product:Optional[ProductOut]

    class Config:
        from_attributes=True




@router.post("/wishlists")
def addWishlist(wishlist:Wishlist_Model,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    
    new_wishlist=Wishlist(
        wishlist_name=wishlist.name,
        user_id=user.id
    )

    db.add(new_wishlist)
    db.commit()
    db.refresh(new_wishlist)

    print("wishlist items:",new_wishlist.wishlist_items)
    return {"status":201,"data":{"wishlist_id":new_wishlist.id,"wishlist_name":new_wishlist.wishlist_name},"message":f"new wishlist {new_wishlist.wishlist_name} added"}


@router.get("/wishlists")
def getWishlists(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    wishlists=db.query(Wishlist).filter(Wishlist.user_id==user.id).all()
    # if len(wishlists)==0:
    #     raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,detail="no wishlist found")
    return wishlists;
    
    pass


@router.delete("/wishlist/{wishlist_id}")
def deleteWishlist(wishlist_id:str,user:User=Depends(get_current_user),db:Session=Depends(get_db)):         

    print(wishlist_id)

    wishlist=db.query(Wishlist).filter(Wishlist.id==wishlist_id, Wishlist.user_id==user.id).first()
    if not wishlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=" wishlist does not exists")
    
    db.delete(wishlist)
    db.commit()

    return {"status":200,"message":"wishlist  deleted successfully" }



@router.post("/wishlist/{wishlist_id}/item")
def addWishlistItem(wishlist_id:str,item:WishlistItemModel,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    
    wishlist=db.query(Wishlist).filter(Wishlist.id==wishlist_id).first()
    if not wishlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=" wishlist does not exists")
    
    product=db.query(Product).filter(Product.id==item.product_id)

    if not product :
        raise HTTPException(status_coode=status.HTTP_404_NOT_FOUND,detail="product does not exists")
    

    new_item=Wishlist_item(
        wishlist_id=wishlist_id,
        product_id=item.product_id
    )

    db.add(new_item)
    product.popularity+=1
    db.commit()
    return {"status":201,"message":" item added to wishlist successfully"}


@router.get("/wishlist/{wishlist_id}/items",response_model=List[WishlistItemOut])
def getWishlistItems(wishlist_id:str,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    wishlist=db.query(Wishlist).filter(Wishlist.id==wishlist_id,Wishlist.user_id==user.id).first()

    if not wishlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="wishlist does not exist")
    

    wishlist_items=(db.query(Wishlist_item).options(joinedload(Wishlist_item.product)).filter(Wishlist_item.wishlist_id==wishlist_id).all())
    return wishlist_items

@router.delete("/wishlist/item/{item_id}")
def deleteWishListItem(item_id:str,user:User=Depends(get_current_user),db:Session=Depends(get_db)):         

    wishlistItem=db.query(Wishlist_item).filter(Wishlist_item.id==item_id).first()
    if not wishlistItem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=" wishlist does not exists")
    
    db.delete(wishlistItem)
    db.commit()

    return {"status":200,"message":"wishlist item deleted successfully" }


