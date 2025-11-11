import uuid
from sqlalchemy import Column,Integer,String,Float,DateTime,func,Boolean,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from  sqlalchemy.orm import relationship
from database import Base


class Used_coupons(Base):
    __tablename__="used_coupons"
    id=Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    coupon_id=Column(ForeignKey("coupons.id"),nullable=True)
    user_id=Column(ForeignKey("users.id"),nullable=True)

    user=relationship("User",back_populates="used_coupons")





class Coupons(Base):
    __tablename__="coupons"
    id=Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    coupon_code=Column(String,unique=True)
    amount=Column(Float,nullable=False,default=0)
    expiry_date=Column(DateTime)
    created_at=Column(DateTime,server_default=func.now())
    order=relationship("Order",back_populates="coupon")