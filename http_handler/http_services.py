import json
import boto3
from boto3.dynamodb.conditions import Attr, Key
from itertools import groupby
from typing import Union
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database import schemas, models
from database.database import dynamodb
from services.services import add_naver_account, add_account_interactions, add_user_session, add_category, get_naver_account, get_account_interactions, get_user_session, get_bot_configs, get_prompt_configs, get_categories, get_logins, get_answer_response, get_question_post, update, delete
from utils import generate_text, convert_date
import os

WEBSOCKET_HANDLER_ARN = os.environ["WEBSOCKET_HANDLER_ARN"]
client = boto3.client('lambda', region_name='ap-southeast-1')

async def send(message, type: str, recipient: str, exclude: str="", group_id: str="", connection_id: str=""):
    outbound_msg = {'invokedRouteKey': 'sendMessage'}
    if not recipient == "all":
        outbound_msg["recipient"] = recipient
    else:
        outbound_msg["recipient"] = "all"
        outbound_msg["exclude"] = exclude
    
    outbound_msg["group_id"] = group_id
    outbound_msg["connection_id"] = connection_id
    
    if type == "task":
        outbound_msg["message"] = {"type": type, "message": message}
    elif type == "response_data":
        outbound_msg["message"] = {"type": type, "data": message}
    elif type == "message":
        outbound_msg["message"] = {"type": type, "response": message}
    
    await invoke(payload=outbound_msg)

async def invoke(payload):
    client.invoke(FunctionName=WEBSOCKET_HANDLER_ARN, InvocationType='RequestResponse', Payload=json.dumps(payload))

async def process_question_answer_form(form: Union[schemas.QuestionAnswerForm_1Q2A, schemas.QuestionAnswerForm_1Q1A], db: Session):
    connections = dynamodb.Table(os.environ["DYNAMO_TABLE"])
    result = connections.scan(FilterExpression=Attr('client_id').ne("autoanswerbot") & Attr('is_active').eq(0))
    result = result["Items"]
    if result:
        result.sort(key=lambda item: item["group_id"])
        grouped_bots = {key: list(group) for key, group in groupby(result, key=lambda bot: bot["group_id"])}
        form = form.model_dump()
        if len(form) == 2:
            filtered_groups = {key: group for key, group in grouped_bots.items() if all(i["connection_id"] != "X" if i["client_id"] != "answerbot_exposure" else i["connection_id"] == "X" for i in group)}
        elif len(form) == 3:
            filtered_groups = {key: group for key, group in grouped_bots.items() if all(i["connection_id"] != "X" for i in group)}
        
        if len(filtered_groups) >= 1:
            group_id, clients = next(iter(filtered_groups.items()))
            await send(recipient="all", message="START", type="task", group_id=group_id)
            botclients = await setup_bot_clients(form, db, group=clients)
        else:
            raise HTTPException(status_code=403, detail="Not all required bot clients are connected!")
    else:
        raise HTTPException(status_code=403, detail="Not all required bot clients are connected!")

    if len(form) == 2:
        await send(recipient="questionbot", message={"question": form['question']['content']}, type="response_data", connection_id=botclients["questionbot"]["connection_id"])
        await send(recipient="answerbot_advertisement", message={"answer_advertisement": form['answer_advertisement']['content']}, type="response_data", connection_id=botclients["answerbot_advertisement"]["connection_id"])

        await send(recipient="questionbot", message="1Q1A", type="response_data", connection_id=botclients["questionbot"]["connection_id"])
    elif len(form) == 3:
        await send(recipient="questionbot", message={"question": form['question']['content']}, type="response_data", connection_id=botclients["questionbot"]["connection_id"])
        await send(recipient="answerbot_advertisement", message={"answer_advertisement": form['answer_advertisement']['content']}, type="response_data", connection_id=botclients["answerbot_advertisement"]["connection_id"])
        await send(recipient="answerbot_exposure", message={"answer_exposure": form['answer_exposure']['content']}, type="response_data", connection_id=botclients["answerbot_exposure"]["connection_id"])

        await send(recipient="questionbot", message="1Q2A", type="response_data", connection_id=botclients["questionbot"]["connection_id"])
    return {"message": "Form received and started automation.", 'bot_clients': botclients}

async def setup_bot_clients(form: dict, db: Session, group: list):
    client_address = {'question': 'questionbot', 'answer_advertisement': 'answerbot_advertisement', 'answer_exposure': 'answerbot_exposure'}
    botclients = {}
    for k, v in form.items():
        account = await get_naver_account(db=db, filters=[models.NaverAccount.status == 0, models.NaverAccount.id == v['id']])
        connection_id, group_id = [(i["connection_id"], i["group_id"]) for i in group if i["client_id"] == client_address[k]][0]
        await send(recipient=client_address[k], message=account.model_dump(), type="response_data", group_id=group_id, connection_id=connection_id)

        user_session = await get_user_session(db=db, filters=[models.UserSession.username == account.username])
        await send(recipient=client_address[k], message=user_session.model_dump(), type="response_data", group_id=group_id, connection_id=connection_id)

        botclients[client_address[k]] = {"connection_id": connection_id, "group_id": group_id}
    
    botconfigs = await get_bot_configs(db=db, filters=[models.BotConfigs.id == 1])
    await send(recipient="all", message=botconfigs.model_dump(), type="response_data", group_id=group[0]["group_id"])
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

async def update_account(updated_data: dict, db: Session):
    id = updated_data.pop("id")
    updated_account = await get_naver_account(db=db, filters=[models.NaverAccount.id == id], schema_validate=False)

    if not updated_account:
        raise HTTPException(status_code=404, detail="Account does not exist!")
    
    if await update(model=models.NaverAccount, data=updated_data, filters={"id": updated_account.id}, db=db):
        return {"message": f"Updated [{updated_account.username}] successfully." }
    else:
        return {"message": f"Failed to update [{updated_account.username}]." }

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
    accounts = await get_naver_account(db=db, fetch_one=False, schema=schemas.NaverAccount)
    joined_list = []
    for index, item in enumerate(interactions):
        item_object = item.model_dump()
        item_object["levelup_id"] = accounts[index].levelup_id
        item_object["status"] = accounts[index].status
        item_object["category"] = accounts[index].category
        item_object["level"] = accounts[index].level
        joined_list.append(item_object)
    return joined_list

async def generate_form_content(db: Session):
    attempts = 0
    while True:
        if attempts >= 3:
            raise HTTPException(status_code=500, detail="There is problem with ChatGPT API as of the moment.")
        question_prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id == 1])
        prohibited_words = [i.strip() for i in question_prompt_configs.prohibited_words.split(';') if i.strip()]
        try:
            question_content = await generate_text(query=question_prompt_configs.query, prompt=question_prompt_configs.prompt, prohibited_words=prohibited_words)
            question_content = json.loads(question_content)
            if type(question_content) is dict and len(question_content) == 2:
                break
            attempts += 1
        except Exception as e:
            print(e)
            attempts += 1

    question = f"{question_content['title']}\n{question_content['content']}"

    answer_advertisement_prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id == 2])
    advertisement_query = answer_advertisement_prompt_configs.query if answer_advertisement_prompt_configs.query else question
    answer_advertisement_content = await generate_text(query=advertisement_query, prompt=answer_advertisement_prompt_configs.prompt, prohibited_words=prohibited_words)

    answer_exposure_prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id == 3])
    exposure_query = answer_exposure_prompt_configs.query if answer_exposure_prompt_configs.query else question
    answer_exposure_content = await generate_text(query=exposure_query, prompt=answer_exposure_prompt_configs.prompt, prohibited_words=prohibited_words)
    return {"question": question_content, "answer_advertisement": answer_advertisement_content, "answer_exposure": answer_exposure_content}

async def fetch_prompt_configs(db: Session):
    question_prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id == 1])
    answer_advertisement_prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id == 2])
    answer_exposure_prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id == 3])
    return {"question": question_prompt_configs, "answer_advertisement": answer_advertisement_prompt_configs, "answer_exposure": answer_exposure_prompt_configs, "prohibited_words": question_prompt_configs.prohibited_words}

async def update_prompt_configs(prompt_configs_update: schemas.PromptConfigsUpdate, db: Session):
    await update(model=models.PromptConfigs, data={"query": prompt_configs_update.question['query'], "prompt": prompt_configs_update.question['prompt'], "prohibited_words": prompt_configs_update.prohibited_words}, filters={"description": "question"}, db=db)
    await update(model=models.PromptConfigs, data={"query": prompt_configs_update.answer_advertisement['query'], "prompt": prompt_configs_update.answer_advertisement['prompt']}, filters={"description": "answer_advertisement"}, db=db)
    return await update(model=models.PromptConfigs, data={"query": prompt_configs_update.answer_exposure['query'], "prompt": prompt_configs_update.answer_exposure['prompt']}, filters={"description": "answer_exposure"}, db=db)

async def fetch_autoanswerbot_configs(db: Session):
    botconfigs = await get_bot_configs(db=db, filters=[models.BotConfigs.id == 2], schema=schemas.BotConfigsStandalone)
    prompt_configs = await get_prompt_configs(db=db, filters=[models.PromptConfigs.id > 3], fetch_one=False)
    levelup_accounts = await get_naver_account(db=db, filters=[models.NaverAccount.category > 1], fetch_one=False, schema=schemas.NaverAccount)
    return {'botconfigs': botconfigs, 'prompt_configs': prompt_configs, 'levelup_accounts': levelup_accounts}

async def update_autoanswerbot_configs(update_config: dict, db: Session):
    botconfigs_id = update_config['botconfigs'].pop("id")
    prompt_id = update_config['prompt_configs'].pop("id")
    botconfigs_update = await update(model=models.BotConfigs, data=update_config['botconfigs'], filters={"id": botconfigs_id}, db=db)
    prompt_update = await update(model=models.PromptConfigs, data=update_config['prompt_configs'], filters={"id": prompt_id}, db=db)
    if botconfigs_update and prompt_update:
        return {'botconfigs': update_config['botconfigs'], 'prompt_configs': update_config['prompt_configs']}

async def fetch_autoanswerbot_connections():
    connections = dynamodb.Table(os.environ["DYNAMO_TABLE"])
    result = connections.scan(FilterExpression=Attr('client_id').eq("autoanswerbot"))
    result = result["Items"]
    return result

async def start_autoanswerbot(autoanswerbot_data: dict, db: Session):
    levelup_accounts = autoanswerbot_data.pop('levelup_accounts')

    not_found_accounts = []
    first_account = None
    for i in levelup_accounts:
        first_account = await get_naver_account(db=db, filters=[models.NaverAccount.id == i], schema_validate=False)
        if first_account:
            first_account = schemas.NaverAccount.model_validate(first_account)
            break
        not_found_accounts.append(i)
    if not first_account:
        raise HTTPException(status_code=404, detail="No matching accounts found!")
    for i in not_found_accounts:
        levelup_accounts.remove(i)
    
    db.query(models.NaverAccount).filter(models.NaverAccount.id.in_(levelup_accounts)).update({"status": 1}, synchronize_session=False)
    db.commit()
    db.close()

    connection_info = autoanswerbot_data.pop('connection_info')
    botconfigs = autoanswerbot_data.pop('botconfigs')
    botconfigs["answers_per_day"] = int(botconfigs["answers_per_day"])
    prompt_configs = autoanswerbot_data.pop('prompt_configs')
    prompt_configs['prohibited_words'] = [i.strip() for i in prompt_configs['prohibited_words'].split(';') if i.strip()]

    connections = dynamodb.Table(os.environ["DYNAMO_TABLE"])
    result = connections.query(KeyConditionExpression=Key("group_id").eq(connection_info['group_id']))
    result = result["Items"]
    if result:
        connection_id = result[0]["connection_id"]
        connections.update_item(Key={"group_id": result[0]["group_id"], "client_id": "autoanswerbot"}, 
                        UpdateExpression="SET account_ids = :account_ids, prompt_configs = :prompt_configs, botconfigs = :botconfigs",
                        ExpressionAttributeValues={":account_ids": levelup_accounts, ":prompt_configs": prompt_configs, ":botconfigs": botconfigs})
    else:
        raise HTTPException(status_code=404, detail="No matching autoanswerbot group_id found!")

    await send(recipient="autoanswerbot", message="START", type="task", connection_id=connection_id)
    await send(recipient='autoanswerbot', message={"account_ids": levelup_accounts}, type="response_data", connection_id=connection_id)

    naver_account = convert_date(first_account.model_dump())
    await send(recipient='autoanswerbot', message=naver_account, type="response_data", connection_id=connection_id)

    user_session = await get_user_session(db=db, filters=[models.UserSession.username == naver_account['username']])
    await send(recipient='autoanswerbot', message=user_session.model_dump(), type="response_data", connection_id=connection_id)

    await send(recipient='autoanswerbot', message=botconfigs, type="response_data", connection_id=connection_id)
    await send(recipient='autoanswerbot', message=prompt_configs, type="response_data", connection_id=connection_id)

async def create_category(category: schemas.CategoryBase, db: Session):
    existing_category = await get_categories(db=db, filters=[models.Categories.category == category.category], schema_validate=False)
    if existing_category:
        raise HTTPException(status_code=403, detail="Same category already exists!")
    return await add_category(category=category, db=db)

async def fetch_categories(db: Session):
    categories = await get_categories(db=db, fetch_one=False)
    return categories

async def update_category(category: schemas.Category, db: Session):
    existing_category = await get_categories(db=db, filters=[models.Categories.id == category.id])
    if existing_category:
        return await update(model=models.Categories, data={"category": category.model_dump()["category"]}, filters={"id": existing_category.model_dump()["id"]}, db=db)

async def delete_category(category_list: list, db: Session):
    categories = await get_categories(db=db, filters=[models.Categories.id.in_(category_list)], fetch_one=False, schema_validate=False)
    success_delete = []
    failed_delete = []

    if categories:
        for category in categories:
            if await delete(model=category, db=db):
                success_delete.append(category.category)
            else:
                failed_delete.append(category.category)
    else:
        raise HTTPException(status_code=404, detail="No matching categories found!")
    return {"success_delete": success_delete, "failed_delete": failed_delete}

async def fetch_activities(db: Session):
    answer_responses = await get_answer_response(db=db, fetch_one=False, schema_validate=False)
    question_posts = await get_question_post(db=db, fetch_one=False, schema_validate=False)
    logins = await get_logins(db=db, fetch_one=False, schema_validate=False)

    return {"logins": logins, "question_posts": question_posts, "answer_responses": answer_responses}