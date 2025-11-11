import uuid
from sqlalchemy import Column,Integer,String,Float,DateTime,func
from sqlalchemy.dialects.postgresql import UUID
from  sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__="users"

    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    email=Column(String,unique=True,nullable=False)
    username=Column(String,unique=True,nullable=False)
    password=Column(String,nullable=False)
    role=Column(String,default="customer")
    created_at=Column(DateTime,server_default=func.now())
    wishlists=relationship("Wishlist",back_populates="user",cascade="all, delete-orphan")
    orders=relationship("Order",back_populates="user",cascade="all, delete-orphan")
    cart=relationship("Cart",back_populates="user",uselist=False)
    used_coupons=relationship("Used_coupons",back_populates="user")
