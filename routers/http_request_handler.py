from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Union, List, Dict
import services.http_services as http_services
from database import schemas, database
from services.authentication import authenticate_user, create_token, get_current_user

class HTTPRequestHandler():
    def __init__(self) -> None:
        self.router = APIRouter()

        @self.router.post("/v1/api/question_answer")
        async def process_question_answer_form(form: Union[schemas.QuestionAnswerForm_1Q2A, schemas.QuestionAnswerForm_1Q1A], db: Session=Depends(database.get_db_conn), authenticated: schemas.Admin=Depends(get_current_user)):
            return await http_services.process_question_answer_form(form, db)
        
        @self.router.post("/v1/api/add_account")
        async def add_account(account: schemas.NaverAccountCreate, db: Session=Depends(database.get_db_conn), authenticated: schemas.Admin=Depends(get_current_user)):
            return await http_services.add_account(account, db)
        
        @self.router.get("/v1/api/accounts")
        async def fetch_accounts(db: Session=Depends(database.get_db_conn), authenticated: schemas.Admin=Depends(get_current_user)):
            return await http_services.fetch_accounts(db)
        
        @self.router.patch("/v1/api/update_account")
        async def update_account(updated_account: Dict, db: Session=Depends(database.get_db_conn), authenticated: schemas.Admin=Depends(get_current_user)):
            return await http_services.update_account(updated_account, db)
        
        @self.router.delete("/v1/api/delete_account")
        async def delete_account(id_list: List[int], db: Session=Depends(database.get_db_conn), authenticated: schemas.Admin=Depends(get_current_user)):
            return await http_services.delete_account(id_list, db)
        
        @self.router.get("/v1/api/interactions")
        async def fetch_accounts(db: Session=Depends(database.get_db_conn), authenticated: schemas.Admin=Depends(get_current_user)):
            return await http_services.fetch_interactions(db)

        @self.router.get("/v1/api/generate_form_content")
        async def generate_form_content(db: Session=Depends(database.get_db_conn), authenticated: schemas.Admin=Depends(get_current_user)):
            return await http_services.generate_form_content(db)
        
        @self.router.get("/v1/api/prompt_configs")
        async def get_prompt_configs(db: Session=Depends(database.get_db_conn), authenticated: schemas.Admin=Depends(get_current_user)):
            return await http_services.fetch_prompt_configs(db)
        
        @self.router.post("/v1/api/prompt_configs")
        async def update_prompt_configs(prompt_configs_update: schemas.PromptConfigsUpdate, db: Session=Depends(database.get_db_conn), authenticated: schemas.Admin=Depends(get_current_user)):
            return await http_services.update_prompt_configs(prompt_configs_update, db)
        
        @self.router.patch("/v1/api/autoanswerbot_prompt")
        async def update_autoanswerbot_prompt(prompt_update: Dict, db: Session=Depends(database.get_db_conn), authenticated: schemas.Admin=Depends(get_current_user)):
            return await http_services.update_autoanswerbot_prompt(prompt_update, db)
        
        @self.router.get("/v1/api/autoanswerbot_configs")
        async def get_autoanswerbot_configs(db: Session=Depends(database.get_db_conn), authenticated: schemas.Admin=Depends(get_current_user)):
            return await http_services.fetch_autoanswerbot_configs(db)
        
        @self.router.post("/v1/api/token")
        async def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db_conn)):
            user = await authenticate_user(form_data.username, form_data.password, db)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid username or password")
            return await create_token(user)
        
        @self.router.get("/v1/api/is_authenticated")
        async def is_authenticated(user: schemas.Admin = Depends(get_current_user)):
            return user