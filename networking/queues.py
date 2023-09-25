import asyncio

class QueuesContainer():
    def __init__(self) -> None:
        self.http_to_websocket = asyncio.Queue(maxsize=1)
        self.websocket_to_database = asyncio.Queue(maxsize=1)
        self.websocket_outbound = asyncio.Queue(maxsize=1)