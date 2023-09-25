class WebsocketService():
    def __init__(self, queues) -> None:
        self.ws_conn_outbound = queues.ws_conn_outbound
        self.ws_service_inbound = queues.ws_service_inbound
        self.ws_service_outbound = queues.ws_service_outbound

    async def process_message(self, message):
        client_id = message['client_id']
        data = message['data']
        await self.ws_conn_outbound.put({"recipient": "all", "exclude": client_id, "message": "[ws service] FROM " + client_id + ": " + data})
    
    async def get_from_ws_service_outbound(self):
        while True:
            outbound_msg = await self.ws_service_outbound.get()
            await self.ws_conn_outbound.put(outbound_msg)
    
    async def get_from_ws_service_inbound(self):
        while True:
            inbound_msg = await self.ws_service_inbound.get()
            await self.process_message(inbound_msg)