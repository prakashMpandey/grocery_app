from fastapi import APIRouter,Depends,HTTPException,status,Response,Form,Request,File,UploadFile,Form
from models.products import Product,Category
from database import get_db
from .authRouter import get_current_user
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session,joinedload
from typing import Annotated,Optional
from .productRouter import manager_required
from pydantic import BaseModel,Field
from models.orders import Order_Item,Order
from models.users import User
from sqlalchemy import func

from sqlalchemy import select

from typing import List

from datetime import datetime
import uuid


router=APIRouter()


class salesReportResponse(BaseModel):
    product_id:Optional[uuid.UUID]=Field(description="id of the product")
    product_name:Optional[str]=Field(description="product name")
    category:Optional[str]=Field(description="product category")
    total_orders:Optional[int]=Field(description="total no of orders placed")
    soldQty:Optional[int]=Field(description="total no of units sold")
    

@router.get("/sales")
async def generateSalesReport(most_sold:Optional[bool]=False,category:Optional[str]=None,user:User=Depends(manager_required),db:Session=Depends(get_db)):

    query = (
    db.query(
        Product,
        Category,
        func.count(Order_Item.id).label("no_of_orders"),
        func.sum(Order_Item.quantity).label("qty_sold")
    )
    .join(Order_Item, Product.id == Order_Item.product_id)
    .join(Category,Product.category_id==Category.id)
    )

    if category:
        cat=db.query(Category).filter(Category.category==category.lower()).first()

        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")

        query=query.filter(Category.id==cat.id)
            
    query=query.group_by(Product.id,Category.id)

    if most_sold:
        query=(query.order_by(func.count(Order_Item.id).desc()))
    else:
        query=(query.order_by(func.count(Order_Item.id)))

    products=query.all()


    # for product,cat,totalOrder,soldQty in products:
    #     print(cat.id)
    result=[
        salesReportResponse(
            product_id=product.id,
            product_name=product.product_name,
            category=cat.category,
            total_orders=totalOrder,
            soldQty=soldQty

        )
        for product,cat,totalOrder,soldQty in products
    ]

    return result

