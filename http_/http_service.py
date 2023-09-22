class HTTPService():
    def __init__(self) -> None:
        pass

    async def process_hello(self, body):
        return {"message": "Received GET request"}
    
    async def process_login(self, body):
        return {"message": "Login process"}
    
    async def process_question_answer_form(self, body):
        return {"message": "Question form received."}