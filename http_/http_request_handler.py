from fastapi import APIRouter, Request
from http_.http_service import HTTPService

class HTTPRequestHandler():
    def __init__(self) -> None:
        self.service = HTTPService()
        self.router = APIRouter()
        
        @self.router.get("/{path:path}")
        async def handle_get_request(request: Request, path: str) -> dict:
            body = await request.body()
            return await self.process_get_request(body, path)
        
        @self.router.post("/{path:path}")
        async def handle_post_request(request: Request, path: str) -> dict:
            body = await request.body()
            return await self.process_post_request(body, path)
    
    async def process_get_request(self, body, path: str) -> dict:
        if path == "":
            return await self.service.process_hello(body)
        
    async def process_post_request(self, body, path: str) -> dict:
        if path == "login":
            return await self.service.process_login(body)
        elif path == "submit_question_form":
            return await self.service.process_question_answer_form(body)