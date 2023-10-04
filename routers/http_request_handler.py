from fastapi import APIRouter, Depends
import services.http_services as http_services
from database import schemas, database
from sqlalchemy.orm import Session

class HTTPRequestHandler():
    def __init__(self) -> None:
        self.router = APIRouter()

        @self.router.post("/v1/api/question_answer")
        async def process_question_answer_form(form: schemas.QuestionAnswerForm, db: Session=Depends(database.get_db_conn)):
            return await http_services.process_question_answer_form(form, db)
        
        @self.router.post("/v1/api/add_account")
        async def add_account(account: schemas.NaverAccountCreate, db: Session=Depends(database.get_db_conn)):
            return await http_services.add_account(account, db)