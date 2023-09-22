from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from http_.http_request_handler import HTTPRequestHandler
from websocket_.websocket_connection_manager import WebsocketConnectionManager
        
class Server:
    def __init__(self):
        self.app = FastAPI()
        self.http_req_handler = HTTPRequestHandler()
        self.websock_conn_manager = WebsocketConnectionManager()

        self.app.include_router(self.http_req_handler.router)
        self.app.include_router(self.websock_conn_manager.router)
        self.app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )

    def run(self):
        import uvicorn
        uvicorn.run("server:server.app", reload=True)

server = Server()
if __name__ == "__main__":
    server.run()
