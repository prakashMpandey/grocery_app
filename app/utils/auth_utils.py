from dotenv import load_dotenv
from pwdlib import PasswordHash
import jwt
import os
from datetime import timedelta,timezone,datetime


password_hash=PasswordHash.recommended()
def getPasswordHash(password:str)->str:

    return password_hash.hash(password)


def verifyPassword(plain_password:str,hashed_password:str)->str:

    if not hashed_password or not isinstance(hashed_password, (str, bytes)):
        return False
    return password_hash.verify(plain_password,hashed_password)



#generates new access token
def createAccessToken(data:dict,expires_delta:timedelta | None=None)->str:


    print(f"hello {dict}") 
    to_encode=data.copy()

    if expires_delta:
        expire=datetime.now(timezone.utc)+ expires_delta
    else:
        expire=datetime.now(timezone.utc)+timedelta(hours=1)
    to_encode.update({"exp":expire})
    secret = os.getenv("ACCESS_TOKEN_SECRET", "defaultsecret")
    algorithm = os.getenv("ALGORITHM", "HS256")
    access_token=jwt.encode(to_encode,secret,algorithm=algorithm)
    
    return access_token
