from database import models, schemas
from database.database import Session, dynamodb
from services.services import get_account_interactions, update, add_answer_response, add_question_post, add_login
from utils import convert_date
import boto3
import json
import os
from boto3.dynamodb.conditions import Key

ENDPOINT_URL = os.environ["ENDPOINT_URL"]
client = boto3.client('apigatewaymanagementapi', region_name='ap-southeast-1', endpoint_url=ENDPOINT_URL)

async def process_incoming_message(client_id, message: dict, connection_id: str="", group_id: str=""):
    if message["type"] == "notification":
        outbound_msg = await create_outbound_message(message=message['data'], recipient=message["send_to"], type="response_data", group_id=group_id)
        response = await send_message(outbound_msg)
    elif message["type"] == "update":
        update_result = await process_update_request(table=message['table'], data=message['data'], filters=message['filters'], db=Session())
        outbound_msg = await create_outbound_message(message=update_result, recipient=client_id, type="message", connection_id=connection_id)
        response = await send_message(outbound_msg)
    elif message["type"] == "logging":
        print(message["log"])
        response = {"statusCode": 200}
    elif message["type"] == "get":
        response = await process_get_request(table=message['table'], filters=message['filters'], client_id=client_id, connection_id=connection_id)
    elif message["type"] == "save":
        response = await process_save_request(table=message['table'], data=message['data'], db=Session())
    elif message["type"] == "update_state":
        response = await process_update_state(client_id=client_id, connection_id=connection_id, state=message["update_state"])
    elif message["type"] == "get_connection_info":
        connections = dynamodb.Table(os.environ["DYNAMO_TABLE"])
        result = connections.query(IndexName="connection_id-client_id-index", 
                                KeyConditionExpression=Key("connection_id").eq(connection_id))
        result = result["Items"]
        if result:
            response = await send_to_client(message={"connection_info": {"group_id": result[0]["group_id"], "connection_id": result[0]["connection_id"]}}, recipient=message["client_id"], connection_id=result[0]["connection_id"])
        else:
            return {"statusCode": 404, "body": f"No matching connection ID!"}
    return response

async def create_outbound_message(message, type: str, recipient: str, exclude: str="", group_id: str="", connection_id: str=""):
    outbound_msg = {}

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
    
    return outbound_msg

async def send_message(outbound_msg):
    if outbound_msg["recipient"] == "all":
        response = await broadcast(exclude=outbound_msg["exclude"], message=outbound_msg["message"], group_id=outbound_msg["group_id"])
    else:
        response = await send_to_client(recipient=outbound_msg["recipient"], message=outbound_msg["message"], connection_id=outbound_msg["connection_id"], group_id=outbound_msg["group_id"])
    return response

async def broadcast(message, exclude: str="", group_id: str=""):
    connections = dynamodb.Table(os.environ["DYNAMO_TABLE"])
    result = connections.query(KeyConditionExpression=Key("group_id").eq(group_id))
    result = result["Items"]
    if result:
        for i in result:
            if i["connection_id"] == "X" or i["client_id"] in exclude:
                continue

            await send_to_client(recipient=i["client_id"], message=message, connection_id=i["connection_id"])
        return {"statusCode": 200}
    else:
        return {"statusCode": 404, "body": f"No matching group ID!"}

async def send_to_client(message, recipient: str, connection_id: str="", group_id: str=""):
    if not connection_id:
        connections = dynamodb.Table(os.environ["DYNAMO_TABLE"])
        result = connections.query(KeyConditionExpression=Key("group_id").eq(group_id) & Key("client_id").eq(recipient))
        result = result["Items"]
        if result:
            connection_id = result[0]["connection_id"]
        else:
            return {"statusCode": 404, "body": f"Connection ID not found!"}

    client.post_to_connection(ConnectionId=connection_id, Data=json.dumps(message).encode('utf-8'))
    return {"statusCode": 200}

async def process_update_state(client_id: str, connection_id: str, state: int):
    if client_id == "autoanswerbot":
        connections = dynamodb.Table(os.environ["DYNAMO_TABLE"])
        result = connections.query(IndexName="connection_id-client_id-index", 
                                KeyConditionExpression=Key("connection_id").eq(connection_id))
        result = result["Items"]
        if result:
            connections.update_item(
                Key={
                    'group_id': result[0]["group_id"],
                    'client_id': result[0]["client_id"]
                },
                UpdateExpression='SET is_active = :is_active',
                ExpressionAttributeValues={
                    ':is_active': state
                }
            )
            return {"statusCode": 200}
    return {"statusCode": 404, "body": f"No {client_id} currently connected!"}

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

async def process_get_request(table: str, filters: dict, client_id: str, connection_id: str):
    response = {"statusCode": 404, "body": f"No matches found!"}
    if table == "naverkin_answer_responses":
        response = await get_answer_response(filters=filters, client_id=client_id, connection_id=connection_id)
    
    return response

async def get_answer_response(filters: dict, client_id: str, connection_id: str):
    results = None
    with Session() as db:
        results = db.query(models.NaverKinAnswerResponse).filter_by(**filters).first()
    
    if results:
        answer_response = schemas.AnswerResponse.model_validate(results)
        answer_response = convert_date(answer_response.model_dump())
        outbound_message = await create_outbound_message(message=answer_response, type="response_data", recipient=client_id)
        await send_to_client(message=outbound_message['message'], recipient=client_id, connection_id=connection_id)
        return {"statusCode": 200}
    else:
        await send_to_client(message=None, recipient=client_id, connection_id=connection_id)
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