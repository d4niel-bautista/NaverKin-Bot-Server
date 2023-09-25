import asyncio

class QueuesContainer():
    def __init__(self) -> None:
        self.ws_service_outbound = asyncio.Queue(maxsize=1)
        self.ws_service_inbound = asyncio.Queue(maxsize=1)
        self.ws_conn_outbound = asyncio.Queue(maxsize=1)