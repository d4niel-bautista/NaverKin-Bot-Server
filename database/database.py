from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import boto3

USER = os.environ["DB_USER"]
PASS = os.environ["DB_PASS"]
HOST = os.environ["DB_HOST"]
PORT = os.environ["DB_PORT"]
NAME = os.environ["DB_NAME"]
DATABASE_URL = f"mysql+pymysql://{USER}:{PASS}@{HOST}:{PORT}/{NAME}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
dynamodb = boto3.resource('dynamodb')

Base = declarative_base()

def get_db_conn():
    db = Session()
    try:
        yield db
    finally:
        db.close()