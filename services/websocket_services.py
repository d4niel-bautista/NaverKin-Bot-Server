from services.queues import ws_conn_outbound
from database import models
import asyncio
from services.services import get_account_interactions, get_bot_configs, get_naver_account, get_user_session, update
from sqlalchemy.orm import Session
from utils import get_string_instances

async def process_incoming_message(client_id, message: dict, db: Session):
    if message["type"] == "notification":
        await send(message=message['data'], recipient=message["send_to"], type="response_data")
    elif message["type"] == "update":
        response = await process_update_request(table=message['table'], data=message['data'], filters=message['filters'], db=db)
        await send(message=response, recipient=client_id, type="message")

async def send(message, type: str, recipient: str, exclude: str=""):
    outbound_msg = {}

    if not recipient == "all":
        outbound_msg["recipient"] = recipient
    else:
        outbound_msg["recipient"] = "all"
        outbound_msg["exclude"] = exclude
    
    if type == "task":
        outbound_msg["message"] = {"type": type, "message": message}
    elif type == "response_data":
        outbound_msg["message"] = {"type": type, "data": message}
    elif type == "message":
        outbound_msg["message"] = {"type": type, "response": message}
    
    await ws_conn_outbound.put(outbound_msg)

async def send_naver_accounts(db: Session):
    await send(recipient="all", message="START", type="task")
    await asyncio.sleep(5)
    
    levelup_account = await get_naver_account(db=db, filters=[models.NaverAccount.levelup_id == 1, models.NaverAccount.status == 0])
    levelup_account_interactions = await get_account_interactions(db=db, filters=[models.AccountInteraction.username == levelup_account.username])
    
    to_skip = []
    while True:
        questionbot_account = await get_naver_account(db=db, filters=[models.NaverAccount.levelup_id == 0, models.NaverAccount.status == 0, models.NaverAccount.username != levelup_account.username, models.NaverAccount.username.not_in(to_skip)])
        questionbot_account_interactions = await get_account_interactions(db=db, filters=[models.AccountInteraction.username == questionbot_account.username])
        if get_string_instances(questionbot_account.username, levelup_account_interactions.interactions) < 1 and get_string_instances(levelup_account_interactions.username, questionbot_account_interactions.interactions) < 1:
            break
        to_skip.append(questionbot_account.username)
        await asyncio.sleep(5)
    
    while True:
        answerbot_account = await get_naver_account(db=db, filters=[models.NaverAccount.levelup_id == 0, models.NaverAccount.status == 0, models.NaverAccount.username != levelup_account.username, models.NaverAccount.username != questionbot_account.username, models.NaverAccount.username.not_in(to_skip)])
        answerbot_account_interactions = await get_account_interactions(db=db, filters=[models.AccountInteraction.username == answerbot_account.username])
        if get_string_instances(answerbot_account.username, questionbot_account_interactions.interactions) < 1 and get_string_instances(questionbot_account.username, answerbot_account_interactions.interactions) < 1:
            break
        to_skip.append(answerbot_account.username)
        await asyncio.sleep(5)
    
    levelup_account_usersession = await get_user_session(db=db, filters=[models.UserSession.username == levelup_account.username])
    questionbot_account_usersession = await get_user_session(db=db, filters=[models.UserSession.username == questionbot_account.username])
    answerbot_account_usersession = await get_user_session(db=db, filters=[models.UserSession.username == answerbot_account.username])

    botconfigs = await get_bot_configs(db=db, filters=[models.BotConfigs.id == 1])

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
    return

async def process_update_request(table: str, data: dict, filters: dict, db: Session):
    if table == "account_interactions":
        return await update_account_interactions(data=data, filters=filters, db=db)
    
    for model in models.Base.__subclasses__():
        if model.__tablename__ == table:
            return await update(model=model, data=data, filters=filters, db=db)
    else:
        return "TABLE NOT FOUND!"

async def update_account_interactions(data: dict, filters: dict, db: Session):
    sender = await get_account_interactions(db=db, filters=[models.AccountInteraction.username == filters['username']])
    sender_interactions = sender.interactions.split(",")
    sender_interactions.append(data['username'])

    target = await get_account_interactions(db=db, filters=[models.AccountInteraction.username == data['username']])
    target_interactions = target.interactions.split(",")
    target_interactions.append(filters['username'])

    sender_interactions = ",".join([i for i in sender_interactions if i])
    target_interactions = ",".join([i for i in target_interactions if i])

    await update(model=models.AccountInteraction, data={"interactions": target_interactions}, filters={"username": data['username']}, db=db)
    return await update(model=models.AccountInteraction, data={"interactions": sender_interactions}, filters={"username": filters['username']}, db=db)