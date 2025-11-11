import uuid
from sqlalchemy import Column,Integer,String,Float,DateTime,func,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from  sqlalchemy.orm import relationship
from database import Base

class Category(Base):

    __tablename__="categories"
    id=Column(Integer,primary_key=True)
    category=Column(String,unique=True,nullable=False)
    
    products=relationship("Product",back_populates="category")


class Product(Base):

    __tablename__="products"
    id=Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    product_name=Column(String,unique=True,nullable=False)
    product_image=Column(String,nullable=True,default="")
    unit_price=Column(Float,nullable=False)
    stock_count=Column(Integer,default=5,nullable=False)
    product_min_stock=Column(Integer,default=5)
    category_id=Column(Integer,ForeignKey("categories.id"),nullable=True)
    popularity=Column(Integer,default=0)
    created_at=Column(DateTime,server_default=func.now())


    category=relationship("Category",back_populates="products")

    cart_items=relationship("Cart_Item",back_populates="product",cascade="all,delete-orphan")
    wishlist_items=relationship("Wishlist_item",back_populates="product",cascade="all,delete-orphan")
    order_items=relationship("Order_Item",back_populates="product",cascade="all,delete-orphan")
    pass