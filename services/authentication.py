from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from services.services import get_admin_account
from database.models import AdminLogin
from database.schemas import Admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/api/token")

async def authenticate_user(username: str, password: str, db: Session):
    user = await get_admin_account(db=db, filters=[AdminLogin.username == username], schema_validate=False)
    if not user:
        return False
    if not user.verify_password(password=password):
        return False
    return Admin.model_validate(user)

async def create_token(user: Admin):
    return {"token": "test"}