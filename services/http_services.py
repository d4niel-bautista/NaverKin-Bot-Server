from database import schemas
import asyncio
async def process_question_answer_form(form: schemas.QuestionAnswerForm):
    from services.websocket_services import send_naver_accounts, send
    await send_naver_accounts()
    await send(recipient="QuestionBot", message={"question": form.question}, type="response_data")
    await asyncio.sleep(1)
    await send(recipient="AnswerBot_Advertisement", message={"answer_advertisement": form.answer_advertisement}, type="response_data")
    await asyncio.sleep(1)
    await send(recipient="AnswerBot_Exposure", message={"answer_exposure": form.answer_exposure}, type="response_data")
    await asyncio.sleep(1)
    return {"message": "Form received and has been sent to bots."}
