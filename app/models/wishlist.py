import uuid
from sqlalchemy import Column,Integer,String,Float,DateTime,func,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from  sqlalchemy.orm import relationship
from database import Base

class Wishlist_item(Base):
        __tablename__="wishlist_items"
        id=Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
        wishlist_id=Column(UUID(as_uuid=True),ForeignKey("wishlists.id"),nullable=False)
        product_id=Column(UUID(as_uuid=True),ForeignKey("products.id"),nullable=False)
        product= relationship("Product",back_populates="wishlist_items")
        wishlist=relationship("Wishlist",back_populates="wishlist_items")
        created_at=Column(DateTime,server_default=func.now())
        

class Wishlist(Base):
        __tablename__="wishlists"
        id=Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
        wishlist_name=Column(String,nullable=False)
        user_id=Column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False)
        user=relationship("User",back_populates="wishlists")
        wishlist_items=relationship("Wishlist_item",back_populates="wishlist",cascade="all ,delete-orphan")
        
        created_at=Column(DateTime,server_default=func.now())