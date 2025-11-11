from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
load_dotenv()

Base=declarative_base()

db_url=os.getenv("DATABASE_URL")
engine=create_engine(db_url)
session=sessionmaker(autocommit=False,autoflush=False,bind=engine)

def get_db():
    db=session()
    try:
        yield db
    finally:
        db.close()
