from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from http_handler import HTTPRequestHandler

class Server:
    def __init__(self):
        self.app = FastAPI()
        self.http_req_handler = HTTPRequestHandler()

        self.app.include_router(self.http_req_handler.router)
        self.app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )

server = Server()
if __name__ == "__main__":
    server.run()
