import json

class WebsocketService():
    def __init__(self, queues) -> None:
        self.queues = queues

    async def process_message(self, message, client_id):
        return {"recipient": "all", "exclude": client_id, "message": "[ws service] FROM " + client_id + ": " + message}
    
    async def get_from_queue(self):
        while True:
            job = await self.queues.http_to_websocket.get()
            await self.queues.websocket_outbound.put(job)
            