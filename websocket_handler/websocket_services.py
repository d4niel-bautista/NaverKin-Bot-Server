from database import models, schemas
from database.database import Session
from services.services import get_account_interactions, update, add_answer_response, add_question_post, add_login
from utils import convert_date
import boto3
import json
from dotenv import load_dotenv
load_dotenv()
import os

ENDPOINT_URL = os.getenv("ENDPOINT_URL")
client = boto3.client('apigatewaymanagementapi', region_name='ap-southeast-1', endpoint_url=ENDPOINT_URL)

async def process_incoming_message(client_id, message: dict):
    if message["type"] == "notification":
        outbound_msg = await create_outbound_message(message=message['data'], recipient=message["send_to"], type="response_data")
        response = await send_message(outbound_msg)
    elif message["type"] == "update":
        update_result = await process_update_request(table=message['table'], data=message['data'], filters=message['filters'], db=Session())
        outbound_msg = await create_outbound_message(message=update_result, recipient=client_id, type="message")
        response = await send_message(outbound_msg)
    elif message["type"] == "logging":
        print(message["log"])
        response = {"statusCode": 200}
    elif message["type"] == "get":
        response = await process_get_request(table=message['table'], filters=message['filters'], client_id=client_id)
    elif message["type"] == "save":
        response = await process_save_request(table=message['table'], data=message['data'], db=Session())
    
    return response

async def create_outbound_message(message, type: str, recipient: str, exclude: str=""):
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
    
    return outbound_msg

async def send_message(outbound_msg):
    if outbound_msg["recipient"] == "all":
        response = await broadcast(exclude=outbound_msg["exclude"], message=outbound_msg["message"])
    else:
        response = await send_to_client(recipient=outbound_msg["recipient"], message=outbound_msg["message"])
    return response

async def broadcast(message, exclude: str=""):
    with Session() as db:
        bot_connections = db.query(models.BotConnections).filter(models.BotConnections.id == 1).first()
    for key, value in bot_connections.__dict__.items():
        if key.startswith("_") or key in exclude or key == "id":
            continue
        if value == "" or value is None:
            continue
        await send_to_client(recipient=key, message=message, connection_id=value)
    return {"statusCode": 200}

async def send_to_client(message, recipient: str, connection_id: str=""):
    if not connection_id:
        with Session() as db:
            bot_connections = db.query(models.BotConnections).filter(models.BotConnections.id == 1).first()
        connection_id = getattr(bot_connections, recipient)

    if connection_id:
        client.post_to_connection(ConnectionId=connection_id, Data=json.dumps(message).encode('utf-8'))
        return {"statusCode": 200}
    else:
        return {"statusCode": 404, "body": f"No {recipient} currently connected!"}

async def process_update_request(table: str, data: dict, filters: dict, db: Session):
    if table == "account_interactions":
        return await update_account_interactions(data=data, filters=filters, db=db)
    
    for model in models.Base.__subclasses__():
        if model.__tablename__ == table:
            return await update(model=model, data=data, filters=filters, db=db)
    else:
        return "TABLE NOT FOUND!"

async def process_save_request(table: str, data: dict, db: Session):
    result = None
    if table == "naverkin_answer_responses":
        result = await add_answer_response(answer=data, db=db)
    elif table == "naverkin_question_posts":
        result = await add_question_post(question=data, db=db)
    elif table == "logins":
        result = await add_login(login=data, db=db)
    
    if result:
        return {"statusCode": 200}
    else:
        return {"statusCode": 502, "body": f"Server error when saving!"}

async def process_get_request(table: str, filters: dict, client_id: str):
    response = {"statusCode": 404, "body": f"No matches found!"}
    if table == "naverkin_answer_responses":
        response = await get_answer_response(filters=filters, client_id=client_id)
    
    return response

async def get_answer_response(filters: dict, client_id: str):
    results = None
    with Session() as db:
        results = db.query(models.NaverKinAnswerResponse).filter_by(**filters).first()
    
    if results:
        answer_response = schemas.AnswerResponse.model_validate(results)
        answer_response = convert_date(answer_response.model_dump())
        outbound_message = await create_outbound_message(message=answer_response, type="response_data", recipient=client_id)
        await send_to_client(message=outbound_message['message'], recipient=client_id)
        return {"statusCode": 200}
    else:
        await send_to_client(message=None, recipient=client_id)
        return {"statusCode": 404, "body": f"No matches found!"}

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