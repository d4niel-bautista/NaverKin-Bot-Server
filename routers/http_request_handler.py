from fastapi import APIRouter
import services.http_services as http_services
from database import schemas

class HTTPRequestHandler():
    def __init__(self) -> None:
        self.router = APIRouter()

        @self.router.post("/v1/api/question_answer")
        async def process_question_answer_form(form: schemas.QuestionAnswerForm):
            return await http_services.process_question_answer_form(form)