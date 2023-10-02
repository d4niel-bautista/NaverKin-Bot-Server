from database import schemas

async def process_question_answer_form(form: schemas.QuestionAnswerForm):
    print(form.model_dump())
    return {"message": "Form received"}
