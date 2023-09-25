from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from http_.http_request_handler import HTTPRequestHandler
from websocket_.websocket_connection_manager import WebsocketConnectionManager
from networking.queues import QueuesContainer
import asyncio

class Server:
    def __init__(self):
        self.app = FastAPI()
        self.queues = QueuesContainer()
        self.http_req_handler = HTTPRequestHandler(self.queues)
        self.websock_conn_manager = WebsocketConnectionManager(self.queues)

        self.app.include_router(self.http_req_handler.router)
        self.app.include_router(self.websock_conn_manager.router)
        self.app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )

        @self.app.on_event("startup")
        async def on_start():
            asyncio.create_task(self.websock_conn_manager.service.get_from_queue())
            asyncio.create_task(self.websock_conn_manager.get_from_outbound_queue())

    def run(self):
        import uvicorn
        uvicorn.run("server:server.app", reload=True)

server = Server()
if __name__ == "__main__":
    server.run()
