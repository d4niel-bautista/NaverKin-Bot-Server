from sqlalchemy.orm import Session
from database import models
from services.queues import ws_conn_outbound
from services.services import get_account_interactions, update, add_answer_response

async def process_incoming_message(client_id, message: dict, db: Session):
    if message["type"] == "notification":
        await send(message=message['data'], recipient=message["send_to"], type="response_data")
    elif message["type"] == "update":
        response = await process_update_request(table=message['table'], data=message['data'], filters=message['filters'], db=db)
        await send(message=response, recipient=client_id, type="message")
    elif message["type"] == "logging":
        print(message["log"])
    elif message["type"] == "save":
        await add_answer_response(message["data"], db=db)

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

async def process_update_request(table: str, data: dict, filters: dict, db: Session):
    if table == "account_interactions":
        return await update_account_interactions(data=data, filters=filters, db=db)
    
    for model in models.Base.__subclasses__():
        if model.__tablename__ == table:
            return await update(model=model, data=data, filters=filters, db=db)
    else:
        return "TABLE NOT FOUND!"

async def process_save_request(table: str, data: dict, db: Session):
    if table == "naverkin_answer_responses":
        return await add_answer_response(answer=data, db=db)

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