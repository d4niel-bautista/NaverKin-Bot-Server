import json
from database.database import dynamic_insert, dynamic_query, dynamic_update, engine
from utils import convert_date

class WebsocketService():
    def __init__(self, queues) -> None:
        self.ws_conn_outbound = queues.ws_conn_outbound
        self.ws_service_inbound = queues.ws_service_inbound
        self.ws_service_outbound = queues.ws_service_outbound

    async def process_message(self, message):
        client_id = message['client_id']
        data = json.loads(message['data'])

        if data['query'] == "get":
            result = await dynamic_query(data['data'], engine)
            await self.ws_conn_outbound.put({"recipient": client_id, "message": {"type": "response_data", "data": result}})
        elif data['query'] == "update":
            result = await dynamic_update(data['data'], engine)
            await self.ws_conn_outbound.put({"recipient": client_id, "message": {"type": "response_data", "data": result}})
        elif data['query'] == "insert":
            result = await dynamic_insert(data['data'], engine)
            await self.ws_conn_outbound.put({"recipient": client_id, "message": {"type": "response_data", "data": result}})
    
    async def get_from_ws_service_outbound(self):
        while True:
            outbound_msg = await self.ws_service_outbound.get()
            if type(outbound_msg) is bytes:
                outbound_msg = json.loads(outbound_msg)
            await self.ws_conn_outbound.put({"recipient": "all", "exclude": "", "message": {"type": "task", "message": "START"}})
    
    async def get_from_ws_service_inbound(self):
        while True:
            inbound_msg = await self.ws_service_inbound.get()
            await self.process_message(inbound_msg)