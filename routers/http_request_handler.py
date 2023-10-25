from fastapi import APIRouter, Depends
import services.http_services as http_services
from database import schemas, database
from sqlalchemy.orm import Session
from typing import Union

class HTTPRequestHandler():
    def __init__(self) -> None:
        self.router = APIRouter()

        @self.router.post("/v1/api/question_answer")
        async def process_question_answer_form(form: Union[schemas.QuestionAnswerForm_1Q1A, schemas.QuestionAnswerForm_1Q2A], db: Session=Depends(database.get_db_conn)):
            return await http_services.process_question_answer_form(form, db)
        
        @self.router.post("/v1/api/add_account")
        async def add_account(account: schemas.NaverAccountCreate, db: Session=Depends(database.get_db_conn)):
            return await http_services.add_account(account, db)
        
        @self.router.get("/v1/api/generate_form_content")
        async def generate_form_content(db: Session=Depends(database.get_db_conn)):
            return await http_services.generate_form_content(db)
        
        @self.router.get("/v1/api/prompt_configs")
        async def get_prompt_configs(db: Session=Depends(database.get_db_conn)):
            return await http_services.fetch_prompt_configs(db)
        
        @self.router.post("/v1/api/prompt_configs")
        async def update_prompt_configs(prompt_configs_update: schemas.PromptConfigsUpdate, db: Session=Depends(database.get_db_conn)):
            return await http_services.update_prompt_configs(prompt_configs_update, db)