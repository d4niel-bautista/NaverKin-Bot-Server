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

async def process_question_answer_form(form: Union[schemas.QuestionAnswerForm_1Q2A, schemas.QuestionAnswerForm_1Q1A], db: Session):
    form = form.model_dump()
    await send(recipient="all", message="START", type="task")
    await asyncio.sleep(1)
    botclients = await setup_bot_clients(form, db)

    if len(form) == 2:
        await send(recipient="QuestionBot", message={"question": form['question']['content']}, type="response_data")
        await asyncio.sleep(1)
        await send(recipient="AnswerBot_Advertisement", message={"answer_advertisement": form['answer_advertisement']['content']}, type="response_data")
        await asyncio.sleep(1)

        await send(recipient="QuestionBot", message="1Q1A", type="response_data")
    elif len(form) == 3:
        await send(recipient="QuestionBot", message={"question": form['question']['content']}, type="response_data")
        await asyncio.sleep(1)
        await send(recipient="AnswerBot_Advertisement", message={"answer_advertisement": form['answer_advertisement']['content']}, type="response_data")
        await asyncio.sleep(1)
        await send(recipient="AnswerBot_Exposure", message={"answer_exposure": form['answer_exposure']['content']}, type="response_data")
        await asyncio.sleep(1)

        await send(recipient="QuestionBot", message="1Q2A", type="response_data")
    return {"message": "Form received and started automation.", 'bot_clients': botclients}

async def setup_bot_clients(form: dict, db: Session):
    client_address = {'question': 'QuestionBot', 'answer_advertisement': 'AnswerBot_Advertisement', 'answer_exposure': 'AnswerBot_Exposure'}
    botclients = {}
    for k, v in form.items():
        account = await get_naver_account(db=db, filters=[models.NaverAccount.status == 0, models.NaverAccount.id == v['id']])
        await send(recipient=client_address[k], message=account.model_dump(), type="response_data")
        await asyncio.sleep(1)
        user_session = await get_user_session(db=db, filters=[models.UserSession.username == account.username])
        await send(recipient=client_address[k], message=user_session.model_dump(), type="response_data")
        await asyncio.sleep(1)
        botclients[k] = account.username
    
    botconfigs = await get_bot_configs(db=db, filters=[models.BotConfigs.id == 1])
    await send(recipient="all", message=botconfigs.model_dump(), type="response_data")
    await asyncio.sleep(1)
    return botclients

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

async def update_account(updated_account: dict, db: Session):
    id = updated_account.pop("id")
    return await update(model=models.NaverAccount, data=updated_account, filters={"id": id}, db=db)

async def delete_account(id_list: list, db: Session):
    naver_accounts = await get_naver_account(db=db, filters=[models.NaverAccount.id.in_(id_list)], fetch_one=False, schema_validate=False)
    success_delete = []
    failed_delete = []

    if naver_accounts:
        for account in naver_accounts:
            if await delete(model=account, db=db):
                success_delete.append(account.username)
            else:
                failed_delete.append(account.username)
    else:
        raise HTTPException(status_code=404, detail="No matching accounts found!")
    return {"success_delete": success_delete, "failed_delete": failed_delete}

async def fetch_interactions(db: Session):
    interactions = await get_account_interactions(db=db, fetch_one=False)
    accounts = await get_naver_account(db=db, fetch_one=False)
    joined_list = []
    for index, item in enumerate(interactions):
        item_object = item.model_dump()
        item_object["levelup_id"] = accounts[index].levelup_id
        item_object["category"] = "category"
        item_object["level"] = "level"
        joined_list.append(item_object)
    return joined_list

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

async def fetch_autoanswerbot_configs(db: Session):
    botconfigs = await get_bot_configs(db=db, filters=[models.BotConfigs.id == 2], schema=schemas.BotConfigsStandalone)
    prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id > 3], fetch_one=False)
    levelup_accounts = await get_naver_account(db=db, filters=[models.NaverAccount.levelup_id == 1, models.NaverAccount.status == 0], fetch_one=False, schema=schemas.NaverAccount)
    return {'botconfigs': botconfigs, 'prompt_configs': prompt_configs, 'levelup_accounts': levelup_accounts}

async def update_autoanswerbot_configs(update_config: dict, db: Session):
    botconfigs_id = update_config['botconfigs'].pop("id")
    prompt_id = update_config['prompt_configs'].pop("id")
    botconfigs_update = await update(model=models.BotConfigs, data=update_config['botconfigs'], filters={"id": botconfigs_id}, db=db)
    prompt_update = await update(model=models.PromptConfigs, data=update_config['prompt_configs'], filters={"id": prompt_id}, db=db)
    if botconfigs_update and prompt_update:
        return {'botconfigs': update_config['botconfigs'], 'prompt_configs': update_config['prompt_configs']}

async def start_autoanswerbot(autoanswerbot_data: dict, db: Session):
    levelup_account = autoanswerbot_data.pop('levelup_account')
    naver_account = await get_naver_account(db=db, filters=[models.NaverAccount.id == levelup_account['id']])
    if not naver_account:
        raise HTTPException(status_code=404, detail=f'Account "{levelup_account["username"]}" does not exist!')
    botconfigs = autoanswerbot_data.pop('botconfigs')
    prompt_configs = autoanswerbot_data.pop('prompt_configs')
    prompt_configs['prohibited_words'] = [i.strip() for i in prompt_configs['prohibited_words'].split('\n') if i]
    await send(recipient="AutoanswerBot", message="START", type="task")
    await asyncio.sleep(1)
    await send(recipient='AutoanswerBot', message=naver_account.model_dump(), type="response_data")
    await asyncio.sleep(1)
    user_session = await get_user_session(db=db, filters=[models.UserSession.username == naver_account.username])
    await send(recipient='AutoanswerBot', message=user_session.model_dump(), type="response_data")
    await asyncio.sleep(1)
    await send(recipient='AutoanswerBot', message=botconfigs, type="response_data")
    await asyncio.sleep(5)
    await send(recipient='AutoanswerBot', message=prompt_configs, type="response_data")