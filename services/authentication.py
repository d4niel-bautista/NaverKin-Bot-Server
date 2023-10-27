from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from services.services import get_admin_account
from database.models import AdminLogin
from database.schemas import Admin
from database.database import get_db_conn
from jose import jwt, JWTError
from dotenv import load_dotenv
load_dotenv()
import os

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/api/token")

async def authenticate_user(username: str, password: str, db: Session):
    user = await get_admin_account(db=db, filters=[AdminLogin.username == username], schema_validate=False)
    if not user:
        return False
    if not user.verify_password(password=password):
        return False
    return Admin.model_validate(user)

async def create_token(user: Admin):
    token = jwt.encode(user.model_dump(), key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user(token: str=Depends(oauth2_scheme), db: Session=Depends(get_db_conn)):
    try:
        payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        id = payload.get("id")
        username = payload.get("username")
        if not id or not username:
            raise HTTPException(
                status_code=401, detail="PAYLOAD ERROR: Could not validate user due to missing properties"
                )
        try:
            return await get_admin_account(db=db, filters=[AdminLogin.id == id, AdminLogin.username == username])
        except:
            raise HTTPException(
                status_code=401, detail="This user does not exist"
                )
    except JWTError:
        raise HTTPException(
            status_code=401, detail="JWT ERROR: Could not decode token"
            )