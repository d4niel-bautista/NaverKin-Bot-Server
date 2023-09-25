class HTTPService():
    def __init__(self, queues) -> None:
        self.ws_service_outbound = queues.ws_service_outbound

    async def process_hello(self, body):
        return {"message": "Received GET request"}
    
    async def process_login(self, body):
        return {"message": "Login process"}
    
    async def process_question_answer_form(self, body):
        await self.ws_service_outbound.put(body.decode())
        return {"message": "Question form received."}