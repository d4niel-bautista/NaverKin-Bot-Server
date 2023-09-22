class WebsocketService():
    def __init__(self) -> None:
        pass

    async def process_message(self, message, client_id):
        return {"recipient": "all", "exclude": client_id, "message": "[ws service] FROM " + client_id + ": " + message}