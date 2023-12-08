from websocket_services import send_message, process_incoming_message
import asyncio
import json
import os
from boto3.dynamodb.conditions import Attr, Key
import string
import random
from database.database import dynamodb

def websocket_handler(event, context):
    print(event)
    route_key = (
        event['requestContext'].pop('routeKey')
        if 'requestContext' in event and 'routeKey' in event['requestContext']
        else event.pop('invokedRouteKey')
        if 'invokedRouteKey' in event
        else None
    )

    body = json.loads(event.pop("body", "{}"))

    if route_key == "$connect":
        response = handle_connection(connection_id=event['requestContext']['connectionId'], bot_client=event['queryStringParameters']['bot'], group_id=event['queryStringParameters']['group_id'])
    elif route_key == "$disconnect":
        response = handle_disconnection(connection_id=event['requestContext']['connectionId'])
    elif route_key == "sendMessage":
        response = asyncio.run(send_message(outbound_msg=event))
    elif route_key == "processMessage":
        if check_matching_connection_id(connection_id=event["requestContext"]["connectionId"], bot_client=body["client_id"]):
            response = asyncio.run(process_incoming_message(client_id=body["client_id"], message=body, connection_id=event["requestContext"]["connectionId"], group_id=body["group_id"]))
        else:
            response = {"statusCode": 403, "body": f'Invalid connection ID!'}
    else:
        response = {"statusCode": 404, "body": "No matching routeKey found!"}
    
    return response

def generate_unique_id(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def handle_connection(connection_id: str, bot_client: str, group_id: str=""):
    connections = dynamodb.Table(os.environ["DYNAMO_TABLE"])
    if group_id:
        result = connections.query(KeyConditionExpression=Key("group_id").eq(group_id))
        if len(result["Items"]) == 3:
            connections.update_item(Key={"group_id": group_id, "client_id": bot_client}, 
                                    UpdateExpression="SET connection_id = :connection_id",
                                    ExpressionAttributeValues={":connection_id": connection_id})
            return {"statusCode": 200}

    if bot_client == "autoanswerbot":
        group_id = generate_unique_id()
        connections.put_item(Item={"group_id": group_id, "client_id": bot_client, "connection_id": connection_id, "username": "", "is_active": 0})
        return {"statusCode": 200}
    else:
        result = connections.scan(FilterExpression=Attr("group_id").ne("") & Attr("client_id").eq(bot_client))
        open_slot = [i for i in result["Items"] if i["connection_id"] == "X"]
        
        if not open_slot:
            question_answer_bots = ["questionbot", "answerbot_advertisement", "answerbot_exposure"]
            other_bots = [i for i in question_answer_bots if i != bot_client]
            group_id = generate_unique_id()
            
            with connections.batch_writer() as batch:
                batch.put_item(Item={"group_id": group_id, "client_id": bot_client, "connection_id": connection_id, "username": "", "is_active": 0})
                for bot in other_bots:
                    batch.put_item(Item={"group_id": group_id, "client_id": bot, "connection_id": "X", "username": "", "is_active": 0})

            return {"statusCode": 200}
        
        connections.update_item(Key={"group_id": open_slot[0]["group_id"], "client_id": open_slot[0]["client_id"]}, 
                                UpdateExpression="SET connection_id = :connection_id",
                                ExpressionAttributeValues={":connection_id": connection_id})
        return {"statusCode": 200}

def handle_disconnection(connection_id: str):
    connections = dynamodb.Table(os.environ["DYNAMO_TABLE"])
    result = connections.query(IndexName="connection_id-client_id-index", 
                               KeyConditionExpression=Key("connection_id").eq(connection_id))
    result = result["Items"]
    
    if result[0]["client_id"] == "autoanswerbot":
        connections.delete_item(Key={"group_id": result[0]["group_id"], "client_id": result[0]["client_id"]})
    else:
        group = connections.query(KeyConditionExpression=Key("group_id").eq(result[0]["group_id"]))
        group = group["Items"]
        is_last_item = all(i["connection_id"] == "X" for i in group if i["client_id"] != result[0]["client_id"])
        if is_last_item:
            with connections.batch_writer() as batch:
                for item in group:
                    batch.delete_item(Key={"group_id": item["group_id"], "client_id": item["client_id"]})
        else:
            connections.update_item(Key={"group_id": result[0]["group_id"], "client_id": result[0]["client_id"]}, 
                                UpdateExpression="SET connection_id = :connection_id",
                                ExpressionAttributeValues={":connection_id": "X"})
    return {"statusCode": 200}

def check_matching_connection_id(connection_id: str, bot_client: str):
    connections = dynamodb.Table(os.environ["DYNAMO_TABLE"])
    result = connections.query(IndexName="connection_id-client_id-index", 
                               KeyConditionExpression=Key("connection_id").eq(connection_id) & Key("client_id").eq(bot_client))
    return True if result["Items"] else False