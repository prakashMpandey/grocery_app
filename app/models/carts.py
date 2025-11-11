import uuid
from sqlalchemy import Column,Integer,String,Float,DateTime,func,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from  sqlalchemy.orm import relationship
from database import Base


class Cart_Item(Base):
    __tablename__="cart_items"
    id=Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    cart_id=Column(UUID(as_uuid=True),ForeignKey("carts.id"),nullable=False)
    product_id=Column(UUID(as_uuid=True),ForeignKey("products.id"),nullable=False)
    quantity=Column(Integer,default=1,nullable=False)
    
    cart=relationship("Cart",back_populates="cart_items")
    product=relationship("Product",back_populates="cart_items")
    created_at=Column(DateTime,server_default=func.now())
    

class Cart(Base):
       __tablename__="carts"
       id=Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
       user_id=Column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False)
       created_at=Column(DateTime,server_default=func.now())

       user=relationship("User",back_populates="cart",uselist=False)
       cart_items=relationship("Cart_Item",back_populates="cart",cascade="all ,delete-orphan")