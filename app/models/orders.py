import uuid
from sqlalchemy import Column,Integer,String,Float,Boolean,DateTime,func,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from  sqlalchemy.orm import relationship
from database import Base

class Order_Item(Base):
    __tablename__ = "order_items"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    sub_total = Column(Float, default=0)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    created_at = Column(DateTime, server_default=func.now())


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, nullable=False)
    total_amount = Column(Float, default=0)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_discount_applied = Column(Boolean, default=False)
    coupon_id = Column(UUID(as_uuid=True), ForeignKey("coupons.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="orders")
    order_items = relationship("Order_Item", back_populates="order", cascade="all, delete-orphan")
    coupon = relationship("Coupons", back_populates="order")
