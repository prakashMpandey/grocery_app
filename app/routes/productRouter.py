from fastapi import APIRouter,Depends,HTTPException,status,Response,Request,File,UploadFile,Form,Query
from models.products import Product,Category
from database import get_db
from .authRouter import get_current_user
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session,joinedload
from typing import Annotated,Optional
from pydantic import BaseModel,Field
from utils.imageUploader import image_uploader
from models.users import User
from sqlalchemy import select,func
from models.orders import Order,Order_Item
from typing import List
import os
import json
import datetime
import uuid

class Product_schema(BaseModel):
    product_name:Optional[str]
    stock_count:Optional[int]
    category:Optional[str]
    product_min_stock:Optional[int]
    unit_price:Optional[float]

    pass


class Product_Response(BaseModel):
    id:str
    product_name:str
    product_image:str
    category:str
    price:float

    class Config:
        orm_mode:True



class CategoryOut(BaseModel):
    id:Optional[int]
    category:Optional[str]

    class Config:
        from_attributes=True
    

class ProductOut(BaseModel):
    id:Optional[uuid.UUID]
    product_name:Optional[str]
    product_image:Optional[str]
    unit_price:Optional[float]
    category:Optional[CategoryOut]
    created_at:Optional[datetime.datetime]
    class Config:
        from_attributes=True

class PaginatedProducts(BaseModel):
    items:List[ProductOut]
    total:int
    page:int
    limit:int

router=APIRouter(tags=['products'])



## check if user is manager or not
def manager_required(user:User=Depends(get_current_user)):
    if user.role!='manager':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='unauthorised access')
    
    return user


@router.post("/products",response_model=Product_Response)
async def addProduct(res:Response,
    product_name:str=Form(...),
            stock_count:int=Form(...,gt=0,description="no of items in stock"),
            unit_price:float=Form(...,gt=0,lt=100000,description="price per unit less than 100000"),
            category:str=Form(...,min_length=1,description="product category"),
            file:UploadFile=File(),
           user:User=Depends(manager_required),db:Session=Depends(get_db),
           ):
    


    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not authenticated")
    
    if not file:
        raise HTTPException(status_code=400,detail="image file is missing")
    

    existing_product=db.query(Product).filter(Product.product_name==product_name).first()

    if existing_product:
        raise HTTPException(status_code=400,detail="product already exists,please update details")
    
    filename,ext=os.path.splitext(file.filename)

    if ext.lower() not in ['.jpeg',".png",".jpg",".webp"]:
        raise HTTPException(status_code=400,detail="please upload a image file")
    
    local_path=f"upload/{file.filename}"
    with open (local_path,"wb") as f:

        try:
            f.write(file.file.read())
            uploadedFileUrl= image_uploader(f"upload/{file.filename}")
        except Exception as e:
            raise Exception(e)
        
        
        

    existing_category=db.query(Category).filter(Category.category==category.lower()).first()


    if not existing_category:
        new_category=Category(category=category.lower())
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        existing_category=new_category   

    new_product = Product(
        product_name=product_name,
        unit_price=unit_price,
        stock_count=int(stock_count),
        product_image=uploadedFileUrl.get("url",""),
        category_id=existing_category.id
    )

    try:
     db.add(new_product)
     db.commit()
     db.refresh(new_product)
    except Exception as e:
     db.rollback()
     raise HTTPException(status_code=500, detail="Failed to add product")

   
    if os.path.exists(local_path):
                os.remove(local_path)


    return Product_Response(
        id=str(new_product.id),
        product_image=new_product.product_image,
        product_name=new_product.product_name,
        category=existing_category.category,
        price=new_product.unit_price
    )

    
@router.get("/products",response_model=PaginatedProducts)
async def get_all_Products(page:Optional[int]=Query(1,ge=1),limit:Optional[int]=Query(10,ge=1),category:Optional[str]=None,most_popular:Optional[bool]=False,user:User=Depends(get_current_user),db=Depends(get_db)):
    

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized access")
    

    product_query=db.query(Product)
    
    if  category:
        category_data=db.query(Category).filter(Category.category==category.lower()).first()
        if not category_data:
            return []
        product_query=(product_query.options(joinedload(Product.category)).filter(Product.category_id==category_data.id))
 

    if most_popular:
        product_query=product_query.order_by(Product.popularity.desc())
    

    offset=(page-1)*limit

    products= product_query.offset(offset).limit(limit).all()
    
    if not products:
        raise HTTPException(
        status_code=404,
        detail="No products found for given filters."
    )

    return PaginatedProducts(
        items=products,
        total=len(products),
        limit=limit,
        page=page

    )

    
    
@router.delete("/products/{product_id}")
async def deleteProduct(product_id:str,user:User=Depends(manager_required),db:Session=Depends(get_db)):
    if not user:
        raise HTTPException(status_code=status.HTPP_401_UNAUTHORIZED,detail='unauthorized access')
    
    print(product_id)
    product=db.query(Product).filter(Product.id==product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no product found")
    
    db.delete(product)
    db.commit()

    return {"status":200,"success":True,"message":"product deleted succesfully"}

   
@router.post("/products/{product_id}")
async def updateProduct(product_id:str,product:Product_schema,user:User=Depends(manager_required),db:Session=Depends(get_db)):

    db_product=db.query(Product).filter(Product.id==product_id).first()


    if  db_product:
        category_data=db.query(Category).filter(Category.category==product.category).first()

        if not category_data:
            db.add(Category(category=product.category))
            db.commit
            db.refresh(category_data)
            pass

        db_product.product_name=product.product_name
        db_product.stock_count=product.stock_count
        db_product.unit_price=product.unit_price
        db_product.product_min_stock=product.product_min_stock
        db_product.unit_of_measure=product.unit_of_measure
        db_product.category_id=category_data.category_id
        db.commit()
        return {"status":200,"success":True,"message":"product updated successfully"}
    
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="product does not exists")


@router.get("/product/{product_id}",response_model=ProductOut)
async def get_single_product(product_id:str,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    try: 
        db_product=db.query(Product).options(joinedload(Product.category)).filter(Product.id==product_id).first()

        if not db_product:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="product does not exists")
     
        else:
            return db_product
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{e.__str__()}")


        

    
   
    
   




