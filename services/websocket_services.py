from services.queues import ws_conn_outbound
from database import models, database, schemas
from sqlalchemy.orm import Session
from sqlalchemy import and_
import asyncio

async def process_incoming_message(client_id, message):
    await send(message=message, recipient=client_id)

async def send(message, type: str, recipient: str, exclude: str=""):
    outbound_msg = {}
    
    if not recipient == "all":
        outbound_msg["recipient"] = recipient
    else:
        outbound_msg["recipient"] = "all"
        outbound_msg["exclude"] = exclude
    
    if type == "task":
        outbound_msg["message"] = {"type": "task", "message": message}
    elif type == "response_data":
        outbound_msg["message"] = {"type": "response_data", "data": message}
    
    await ws_conn_outbound.put(outbound_msg)

async def get_naver_account(levelup: bool, filters: list = [], db: Session=next(database.get_db_conn())):
    return schemas.NaverAccount.model_validate(db.query(models.NaverAccount).filter(and_(models.NaverAccount.status == 0, models.NaverAccount.levelup_id == 1)).filter(*filters).first())\
            if levelup else\
            schemas.NaverAccount.model_validate(db.query(models.NaverAccount).filter(models.NaverAccount.status == 0).filter(*filters).first())

async def get_account_interactions(username: str, filters: list = [], db: Session=next(database.get_db_conn())):
    return schemas.AccountInteraction.model_validate(db.query(models.AccountInteraction).filter(models.AccountInteraction.username == username).filter(*filters).first())

async def get_user_session(username: str, db: Session=next(database.get_db_conn())):
    return schemas.UserSession.model_validate(db.query(models.UserSession).filter(models.UserSession.username == username).first())

async def get_bot_configs(botconfigs_id: int=1, db: Session=next(database.get_db_conn())):
    return schemas.BotConfigs.model_validate(db.query(models.BotConfigs).filter(models.BotConfigs.id == botconfigs_id).first())

async def send_naver_accounts():
    from utils import get_string_instances

    await send(recipient="all", message="START", type="task")
    await asyncio.sleep(5)
    
    levelup_account = await get_naver_account(levelup=True)
    levelup_account_interactions = await get_account_interactions(username=levelup_account.username)
    
    to_skip = []
    while True:
        questionbot_account = await get_naver_account(levelup=False, filters=[models.NaverAccount.username != levelup_account.username, models.NaverAccount.username.not_in(to_skip)])
        questionbot_account_interactions = await get_account_interactions(username=questionbot_account.username)
        if get_string_instances(questionbot_account.username, levelup_account_interactions.interactions) < 1 and get_string_instances(levelup_account_interactions.username, questionbot_account_interactions.interactions) < 1:
            break
        to_skip.append(questionbot_account.username)
        await asyncio.sleep(5)
    
    while True:
        answerbot_account = await get_naver_account(levelup=False, filters=[models.NaverAccount.username != levelup_account.username, models.NaverAccount.username != questionbot_account.username, models.NaverAccount.username.not_in(to_skip)])
        answerbot_account_interactions = await get_account_interactions(username=answerbot_account.username)
        if get_string_instances(answerbot_account.username, questionbot_account_interactions.interactions) < 1 and get_string_instances(questionbot_account.username, answerbot_account_interactions.interactions) < 1:
            break
        to_skip.append(answerbot_account.username)
        await asyncio.sleep(5)
    
    levelup_account_usersession = await get_user_session(username=levelup_account.username)
    questionbot_account_usersession = await get_user_session(username=questionbot_account.username)
    answerbot_account_usersession = await get_user_session(username=answerbot_account.username)

    botconfigs = await get_bot_configs()

    await send(recipient="AnswerBot_Exposure", message=levelup_account.model_dump(), type="response_data")
    await asyncio.sleep(1)
    await send(recipient="QuestionBot", message=questionbot_account.model_dump(), type="response_data")
    await asyncio.sleep(1)
    await send(recipient="AnswerBot_Advertisement", message=answerbot_account.model_dump(), type="response_data")
    await asyncio.sleep(5)

    await send(recipient="AnswerBot_Exposure", message=levelup_account_usersession.model_dump(), type="response_data")
    await asyncio.sleep(1)
    await send(recipient="QuestionBot", message=questionbot_account_usersession.model_dump(), type="response_data")
    await asyncio.sleep(1)
    await send(recipient="AnswerBot_Advertisement", message=answerbot_account_usersession.model_dump(), type="response_data")
    await asyncio.sleep(5)

    await send(recipient="all", message=botconfigs.model_dump(), type="response_data")