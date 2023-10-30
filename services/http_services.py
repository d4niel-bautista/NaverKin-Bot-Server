import asyncio
import json
from typing import Union
from fastapi import HTTPException
from pydantic_core import ValidationError
from sqlalchemy.orm import Session
from database import schemas, models
from services.services import add_naver_account, add_account_interactions, add_user_session, get_naver_account, get_account_interactions, get_user_session, get_bot_configs, get_prompt_configs, update, delete
from utils import get_string_instances, generate_text
from services.websocket_services import send

async def process_question_answer_form(form: Union[schemas.QuestionAnswerForm_1Q1A, schemas.QuestionAnswerForm_1Q2A], db: Session):
    await send(recipient="all", message="START", type="task")

    if isinstance(form, schemas.QuestionAnswerForm_1Q1A):
        response = await send_accounts_1Q1A(db=db)

        await asyncio.sleep(5)
        await send(recipient="QuestionBot", message={"question": form.question}, type="response_data")
        await asyncio.sleep(1)
        await send(recipient="AnswerBot_Advertisement", message={"answer_advertisement": form.answer}, type="response_data")
        await asyncio.sleep(1)

        await send(recipient="QuestionBot", message="1Q1A", type="response_data")
    elif isinstance(form, schemas.QuestionAnswerForm_1Q2A):
        response = await send_accounts_1Q2A(db=db)

        await asyncio.sleep(5)
        await send(recipient="QuestionBot", message={"question": form.question}, type="response_data")
        await asyncio.sleep(1)
        await send(recipient="AnswerBot_Advertisement", message={"answer_advertisement": form.answer_advertisement}, type="response_data")
        await asyncio.sleep(1)
        await send(recipient="AnswerBot_Exposure", message={"answer_exposure": form.answer_exposure}, type="response_data")
        await asyncio.sleep(1)

        await send(recipient="QuestionBot", message="1Q2A", type="response_data")
    return response

async def send_accounts_1Q1A(db: Session):
    try:
        questionbot_account = await get_naver_account(db=db, filters=[
            models.NaverAccount.levelup_id == 0, 
            models.NaverAccount.status == 0])
        questionbot_account_interactions = await get_account_interactions(db=db, filters=[
            models.AccountInteraction.username == questionbot_account.username])

        to_skip = []
        while True:
                answerbot_account = await get_naver_account(db=db, filters=[
                    models.NaverAccount.levelup_id == 0, 
                    models.NaverAccount.status == 0, 
                    models.NaverAccount.username != questionbot_account.username, 
                    models.NaverAccount.username.not_in(to_skip)])
                answerbot_account_interactions = await get_account_interactions(db=db, filters=[
                    models.AccountInteraction.username == answerbot_account.username])
                if get_string_instances(answerbot_account.username, questionbot_account_interactions.interactions) < 1 and get_string_instances(questionbot_account.username, answerbot_account_interactions.interactions) < 1:
                    break
                to_skip.append(answerbot_account.username)
                await asyncio.sleep(2)

        questionbot_account_usersession = await get_user_session(db=db, filters=[
            models.UserSession.username == questionbot_account.username])
        answerbot_account_usersession = await get_user_session(db=db, filters=[
            models.UserSession.username == answerbot_account.username])

        botconfigs = await get_bot_configs(db=db, filters=[models.BotConfigs.id == 1])

        await asyncio.sleep(1)
        await send(recipient="QuestionBot", message=questionbot_account.model_dump(), type="response_data")
        await asyncio.sleep(1)
        await send(recipient="AnswerBot_Advertisement", message=answerbot_account.model_dump(), type="response_data")
        await asyncio.sleep(5)

        await asyncio.sleep(1)
        await send(recipient="QuestionBot", message=questionbot_account_usersession.model_dump(), type="response_data")
        await asyncio.sleep(1)
        await send(recipient="AnswerBot_Advertisement", message=answerbot_account_usersession.model_dump(), type="response_data")
        await asyncio.sleep(5)

        await send(recipient="all", message=botconfigs.model_dump(), type="response_data")
        return {"message": "Form received and started automation.", "question_bot": questionbot_account, "answer_bot": answerbot_account}
    except ValidationError:
        accounts = [account.model_dump_json() for account in await get_account_interactions(db=db, fetch_one=False)]
        if not accounts:
            raise HTTPException(status_code=500, detail="No existing accounts in the database.")
        raise HTTPException(status_code=500, detail="There is not enough accounts to start the automation or all accounts have already interacted with each other.\n" + "\n".join(accounts))

async def send_accounts_1Q2A(db: Session):
    try:
        levelup_account = await get_naver_account(db=db, filters=[
            models.NaverAccount.levelup_id == 1, 
            models.NaverAccount.status == 0])
        levelup_account_interactions = await get_account_interactions(db=db, filters=[
            models.AccountInteraction.username == levelup_account.username])
        
        to_skip = []
        while True:
            questionbot_account = await get_naver_account(db=db, filters=[
                models.NaverAccount.levelup_id == 0, 
                models.NaverAccount.status == 0, 
                models.NaverAccount.username != levelup_account.username, 
                models.NaverAccount.username.not_in(to_skip)])
            questionbot_account_interactions = await get_account_interactions(db=db, filters=[
                models.AccountInteraction.username == questionbot_account.username])
            if get_string_instances(questionbot_account.username, levelup_account_interactions.interactions) < 1 and get_string_instances(levelup_account_interactions.username, questionbot_account_interactions.interactions) < 1:
                break
            to_skip.append(questionbot_account.username)
            await asyncio.sleep(2)
        
        while True:
            answerbot_account = await get_naver_account(db=db, filters=[
                models.NaverAccount.levelup_id == 0, 
                models.NaverAccount.status == 0, 
                models.NaverAccount.username != levelup_account.username, 
                models.NaverAccount.username != questionbot_account.username, 
                models.NaverAccount.username.not_in(to_skip)])
            answerbot_account_interactions = await get_account_interactions(db=db, filters=[
                models.AccountInteraction.username == answerbot_account.username])
            if get_string_instances(answerbot_account.username, questionbot_account_interactions.interactions) < 1 and get_string_instances(questionbot_account.username, answerbot_account_interactions.interactions) < 1:
                break
            to_skip.append(answerbot_account.username)
            await asyncio.sleep(2)
        
        levelup_account_usersession = await get_user_session(db=db, filters=[
            models.UserSession.username == levelup_account.username])
        questionbot_account_usersession = await get_user_session(db=db, filters=[
            models.UserSession.username == questionbot_account.username])
        answerbot_account_usersession = await get_user_session(db=db, filters=[
            models.UserSession.username == answerbot_account.username])

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
        return {"message": "Form received and started automation.", "question_bot": questionbot_account, "answer_bot_exposure": levelup_account, "answer_bot_advertisement": answerbot_account}
    except ValidationError:
        accounts = [account.model_dump_json() for account in await get_account_interactions(db=db, fetch_one=False)]
        if not accounts:
            raise HTTPException(status_code=500, detail="No existing accounts in the database.")
        raise HTTPException(status_code=500, detail="There is not enough accounts to start the automation or all accounts have already interacted with each other.\n" + "\n".join(accounts))

async def add_account(account: schemas.NaverAccountCreate, db: Session):
    try:
        naver_account = await get_naver_account(db=db, filters=[models.NaverAccount.username == account.model_dump()["username"]])
    except:
        naver_account = None
    
    if naver_account:
        raise HTTPException(status_code=403, detail=f'Account with username "{naver_account.username}" already exists!')

    added_account = await add_naver_account(db=db, account=account)
    await add_user_session(account=added_account, db=db)
    await add_account_interactions(account=added_account, db=db)
    return added_account

async def fetch_accounts(db: Session):
    return await get_naver_account(db=db, fetch_one=False, schema=schemas.NaverAccount)

async def update_account(updated_account: schemas.NaverAccount, db: Session):
    updated_account = updated_account.model_dump()
    id = updated_account.pop("id")
    return await update(model=models.NaverAccount, data=updated_account, filters={"id": id}, db=db)

async def delete_account(delete_account: schemas.NaverAccountDelete, db: Session):
    naver_account = await get_naver_account(db=db, filters=[models.NaverAccount.id == delete_account.model_dump()['id'], models.NaverAccount.username == delete_account.model_dump()['username']], schema_validate=False)
    if not naver_account:
        raise HTTPException(status_code=404, detail=f'Account "{delete_account.model_dump()["username"]}" does not exist.')
    return await delete(model=naver_account, db=db)

async def generate_form_content(db: Session):
    attempts = 0
    while True:
        if attempts >= 3:
            raise HTTPException(status_code=500, detail="There is problem with ChatGPT API as of the moment.")
        question_prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id == 1])
        prohibited_words = [i for i in question_prompt_configs.prohibited_words.split(',') if i]
        try:
            question_content = await generate_text(query=question_prompt_configs.query, prompt=question_prompt_configs.prompt, prohibited_words=prohibited_words)
            question_content = json.loads(question_content)
            if type(question_content) is dict and len(question_content) == 2:
                break
            await asyncio.sleep(1)
            attempts += 1
        except Exception as e:
            print(e)
            attempts += 1

    question = f"{question_content['title']}\n{question_content['content']}"

    answer_advertisement_prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id == 2])
    answer_advertisement_content = await generate_text(query=question, prompt=answer_advertisement_prompt_configs.prompt, prohibited_words=prohibited_words)

    answer_exposure_prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id == 3])
    answer_exposure_content = await generate_text(query=question, prompt=answer_exposure_prompt_configs.prompt, prohibited_words=prohibited_words)
    return {"question": question_content, "answer_advertisement": answer_advertisement_content, "answer_exposure": answer_exposure_content}

async def fetch_prompt_configs(db: Session):
    question_prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id == 1])
    answer_advertisement_prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id == 2])
    answer_exposure_prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id == 3])
    prohibited_words = "\n".join([i for i in question_prompt_configs.prohibited_words.split(',') if i])
    return {"question": question_prompt_configs, "answer_advertisement": answer_advertisement_prompt_configs, "answer_exposure": answer_exposure_prompt_configs, "prohibited_words": prohibited_words}

async def update_prompt_configs(prompt_configs_update: schemas.PromptConfigsUpdate, db: Session):
    prohibited_words = ",".join([i.strip() for i in prompt_configs_update.prohibited_words.split("\n") if i])
    await update(model=models.PromptConfigs, data={"query": prompt_configs_update.question['query'], "prompt": prompt_configs_update.question['prompt'], "prohibited_words": prohibited_words}, filters={"description": "question"}, db=db)
    await update(model=models.PromptConfigs, data={"query": prompt_configs_update.answer_advertisement['query'], "prompt": prompt_configs_update.answer_advertisement['prompt']}, filters={"description": "answer_advertisement"}, db=db)
    return await update(model=models.PromptConfigs, data={"query": prompt_configs_update.answer_exposure['query'], "prompt": prompt_configs_update.answer_exposure['prompt']}, filters={"description": "answer_exposure"}, db=db)