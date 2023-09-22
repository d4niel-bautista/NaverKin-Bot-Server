from fastapi import APIRouter, Request, Form

class HTTPRequestHandler():
    def __init__(self) -> None:
        self.router = APIRouter()
        
        @self.router.get("/{path:path}")
        async def handle_get_request(request: Request, path: str) -> dict:
            return {'message': 'Received GET request', 'origin': request.headers["origin"]}
        
        @self.router.post("/{path:path}")
        async def handle_post_request(request: Request, path: str) -> dict:
            if path == "login":
                return await self.login(request)
    
    async def login(self, request: Request) -> dict:
        return await request.json()