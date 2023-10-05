from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from datetime import datetime
import services.websocket_services as ws_services
from database import database
from sqlalchemy.orm import Session

class WebsocketConnectionManager():
    def __init__(self, queue) -> None:
        self.router = APIRouter()
        self.ws_conn_outbound = queue
        self.clients = {}

        @self.router.websocket('/{client_id}')
        async def handle_connection(websocket: WebSocket, client_id: str, db: Session=Depends(database.get_db_conn)):
            await websocket.accept()
            
            if client_id not in self.clients.keys():
                self.clients[client_id] = websocket
            await self.client_state_update(client_id, 1)

            try:
                while True:
                    data = await websocket.receive_json()
                    await ws_services.process_incoming_message(client_id, data, db=db)
            except WebSocketDisconnect:
                await self.client_state_update(client_id, 0)
                del self.clients[client_id]
        
    async def get_from_ws_conn_outbound(self):
        while True:
            outbound_msg = await self.ws_conn_outbound.get()
            print(outbound_msg)
            await self.send(outbound_msg)
    
    async def client_state_update(self, client_id: str, state: int):
        current_date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if state:
            print(f"[{current_date_time}] {client_id} has connected")
        elif not state:
            print(f"[{current_date_time}] {client_id} has disconnected")
    
    async def send(self, message):
        if message["recipient"] == "all":
            await self.broadcast(exclude=message['exclude'], message=message['message'])
        else:
            await self.send_to_client(recipient=message["recipient"], message=message["message"])

    async def broadcast(self, message, exclude: str=""):
        for client in self.clients:
            if client in exclude:
                continue
            await self.send_to_client(message, client)
    
    async def send_to_client(self, message, recipient: str):
        if not recipient in self.clients.keys():
            return
        await self.clients[recipient].send_json(message)