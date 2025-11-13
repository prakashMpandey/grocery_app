from fastapi import APIRouter,Depends,HTTPException
from database import get_db
from .authRouter import get_current_user
from pydantic import BaseModel,Field
from models.users import User
from models.products import Category
from datetime import datetime
import uuid
from typing import Optional,List

router=APIRouter()


class CategoryReq(BaseModel):
    category:str
    pass


class CategoryRes(BaseModel):
    id:Optional[int] 

    category:Optional[str] 
    
    class Config:
       from_attributes=True
    pass



@router.post("/category/add",tags=["manager"])
def add_Category(categoryData:CategoryReq,user:User=Depends(get_current_user),db=Depends(get_db)):
   try: 
    if user.role!='manager':
        raise HTTPException(status_code=401,detail="only manager is authorized")
    
    existing_category=db.query(Category).filter(Category.category==categoryData.category).first()

    if existing_category:
       raise HTTPException(status_code=400,detail="category already exists")
   
    
    db.add(Category(
       category=categoryData.category
    ))
    db.commit()

    return {"status":200,"success":"true","message":"category added successfully"}
   except Exception as e:
      raise HTTPException(status_code=500,detail=f"{e}")
   

@router.delete("/category/{category_id}",tags=["manager"])
def delete_coupon(category_id:str,user:User=Depends(get_current_user),db=Depends(get_db)):
    try: 
     if user.role!='manager':
        raise HTTPException(status_code=401,detail="only manager is authorized")
     
     category=db.query(Category).filter(Category.id==category_id).first()

     if not category:
        raise HTTPException(status_code=400,detail="no category found")
     
     db.delete(category)
     db.commit()

     return {"status":200,"success":"true","message":"category deleted successfully"}
    except HTTPException as e:
      raise HTTPException(status_code=500,detail="internal server error")

 
@router.get("/categories",response_model=List[CategoryRes],tags=["manager"])
def get_categories(user:User=Depends(get_current_user),db=Depends(get_db)):
    if user.role!='manager':
        raise HTTPException(status_code=401,detail="only manager is authorized")
    
    categories=db.query(Category).all()

    if categories:
       return categories
    
    raise HTTPException(status_code=500,detail="no category found")

    
    