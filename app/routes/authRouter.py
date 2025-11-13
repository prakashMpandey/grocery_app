from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session,load_only
from database import get_db
from models.users import User
from pydantic import EmailStr, BaseModel,Field
from dotenv import load_dotenv
from typing import Literal,Optional
from utils.auth_utils import getPasswordHash,createAccessToken,verifyPassword
import jwt
import os


load_dotenv()
router = APIRouter(prefix="/auth",tags=["customer","manager"])



#structure of signup request
class SignupPayload(BaseModel):
    email: EmailStr=Field(description="email of the user")
    username: str=Field(...,min_length=3,description="username")
    password: str=Field(...,min_length=8,description="password should be min 8 letters")

#structure of signin request
class LoginPayload(BaseModel):
    username_or_email: str
    password: str


# returns current user object
async def get_current_user(req: Request, db: Session = Depends(get_db)):
    token = req.cookies.get("access_token")
    if not token:
        auth_header = req.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")

    try:
        secret = os.getenv("ACCESS_TOKEN_SECRET", "defaultsecret")
        algo = os.getenv("ALGORITHM", "HS256")
        payload = jwt.decode(token, secret, algorithms=[algo])
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="invalid access token")
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")

    user = db.query(User).options(load_only(User.id,User.email,User.username,User.role,User.created_at)).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user



@router.post("/signup",)

def signup(payload: SignupPayload, db: Session = Depends(get_db)):
    email = str(payload.email)
    existing_user = db.query(User).filter((User.email == email) | (User.username == payload.username)).first()


    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user already exists")
    

    new_user = User(email=email, password=getPasswordHash(payload.password), username=payload.username)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    user_dict = new_user.__dict__.copy()
    user_dict.pop("password", None)
    return {"status": 200, "success": True, "data": user_dict, "message": "user created successfully"}


@router.post("/login")
def login(payload: LoginPayload, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter((User.username == payload.username_or_email) | (User.email == payload.username_or_email)).first()

    if not user or not verifyPassword(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    access_token = createAccessToken(data={"id": str(user.id), "email": user.email})
    res = JSONResponse(status_code=200, content={"status": 200, "success": True, "message": "user logged in successfully"})
    res.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, max_age=3600)
    return res


@router.post("/logout")
def logout(res: Response, user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid login")

    res = JSONResponse(status_code=200, content={"status": 200, "succes": True, "message": "user logged out successfully"})
    res.delete_cookie("access_token")
    return res




