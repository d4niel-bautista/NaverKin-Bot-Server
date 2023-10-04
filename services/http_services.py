from database import schemas, models, database
import asyncio
from services.services import add_naver_account, add_account_interactions, add_user_session
from fastapi import HTTPException
from sqlalchemy.orm import Session

async def process_question_answer_form(form: schemas.QuestionAnswerForm, db: Session):
    from services.websocket_services import send_naver_accounts, send
    await send_naver_accounts(db=db)
    await asyncio.sleep(5)
    await send(recipient="QuestionBot", message={"question": form.question}, type="response_data")
    await asyncio.sleep(1)
    await send(recipient="AnswerBot_Advertisement", message={"answer_advertisement": form.answer_advertisement}, type="response_data")
    await asyncio.sleep(1)
    await send(recipient="AnswerBot_Exposure", message={"answer_exposure": form.answer_exposure}, type="response_data")
    await asyncio.sleep(1)
    return {"message": "Form received and has been sent to bots."}

async def add_account(account: schemas.NaverAccountCreate, db: Session):
    naver_account = db.query(models.NaverAccount).filter(models.NaverAccount.username == account.model_dump()["username"]).first()
    if naver_account:
        raise HTTPException(status_code=403, detail=f'Account with username "{naver_account.username}" already exists!')

    added_account = await add_naver_account(db=db, account=account)
    await add_user_session(account=added_account, db=db)
    await add_account_interactions(account=added_account, db=db)
    return added_account
