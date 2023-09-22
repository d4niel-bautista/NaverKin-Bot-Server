from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime

class WebsocketConnectionManager():
    def __init__(self) -> None:
        self.router = APIRouter()
        self.clients = {}

        @self.router.websocket('/{client_id}')
        async def handle_connection(websocket: WebSocket, client_id: str):
            await websocket.accept()
            
            if client_id not in self.clients.keys():
                self.clients[client_id] = websocket
            await self.client_state_update(client_id, 1)

            try:
                while True:
                    data = await websocket.receive_text()
                    
                    await self.broadcast(data, exclude=client_id)
            except WebSocketDisconnect:
                await self.client_state_update(client_id, 0)
                del self.clients[client_id]
                print(self.clients)
    
    async def client_state_update(self, client_id: str, state: int):
        current_date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if state:
            print(f"[{current_date_time}] {client_id} has connected")
        elif not state:
            print(f"[{current_date_time}] {client_id} has disconnected")

    async def broadcast(self, message, exclude: str=""):
        for client in self.clients:
            if client == exclude:
                continue
            await self.clients[client].send_text("FROM " + exclude + ": " + message)
    
    async def send_to_client(self, message, target: str):
        for client in self.clients:
            if client != target:
                continue
            await self.clients[client].send_text(message)
            break