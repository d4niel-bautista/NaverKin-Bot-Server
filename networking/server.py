from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routers import HTTPRequestHandler, WebsocketConnectionManager
from services import queues
import asyncio

class Server:
    def __init__(self):
        self.app = FastAPI()
        self.http_req_handler = HTTPRequestHandler()
        self.websock_conn_manager = WebsocketConnectionManager(queue=queues.ws_conn_outbound)

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
            asyncio.create_task(self.websock_conn_manager.get_from_ws_conn_outbound())

server = Server()
if __name__ == "__main__":
    server.run()
