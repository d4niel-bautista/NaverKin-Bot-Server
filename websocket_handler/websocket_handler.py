from websocket_services import process_incoming_message
from database.models import BotConnections
from database.database import Session
import asyncio

def websocket_handler(event, context):
    route_key = (
        event['requestContext']['routeKey']
        if 'requestContext' in event and 'routeKey' in event['requestContext']
        else event.get('invokedRouteKey')
        if 'invokedRouteKey' in event
        else None
    )

    if route_key == "$connect":
        response = asyncio.run(handle_connection(connection_id=event['requestContext']['connectionId'], bot_client=event['queryStringParameters']['bot']))
    elif route_key == "$disconnect":
        response = asyncio.run(handle_disconnection(connection_id=event['requestContext']['connectionId']))
    else:
        response = {"statusCode": 404, "body": "No matching routeKey found!"}
    
    return response

async def handle_connection(connection_id: str, bot_client: str):
    with Session() as db:
        bot_connections = db.query(BotConnections).filter(BotConnections.id == 1).first()
        current_connection_id = getattr(bot_connections, bot_client)

        if current_connection_id == '' or current_connection_id is None:
            db.query(BotConnections).filter(BotConnections.id == 1).update({bot_client: connection_id})
            db.commit()
            return {"statusCode": 200}
        else:
            return {"statusCode": 403, "body": f'There is an existing connection for "{bot_client}"!\n[CURRENT] {bot_client}={current_connection_id}'}

async def handle_disconnection(connection_id: str):
    with Session() as db:
        bot_connections = db.query(BotConnections).filter(BotConnections.id == 1).first()
        bot_client = None
        for key, value in bot_connections.__dict__.items():
            if key.startswith("_"):
                continue
            if value == connection_id:
                bot_client = key
                break

        if bot_client:
            db.query(BotConnections).filter(BotConnections.id == 1).update({bot_client: ''})
            db.commit()
            return {"statusCode": 200}
        else:
            return {"statusCode": 404, "body": f'No matching connection ID found!'}