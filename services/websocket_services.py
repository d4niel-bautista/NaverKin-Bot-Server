from services.queues import ws_conn_outbound
from database import models
import asyncio
from services.services import get_account_interactions, get_bot_configs, get_naver_account, get_user_session
from sqlalchemy.orm import Session

async def process_incoming_message(client_id, message: dict, db: Session):
    if message["type"] == "notification":
        await send(message=message['data'], recipient=message["send_to"], type="response_data")
    else:
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

async def send_naver_accounts(db: Session):
    from utils import get_string_instances

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