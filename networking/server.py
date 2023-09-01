import socket
import threading
import os
from .client_handler import ClientHandler
from utils import get_logger
from dotenv import load_dotenv
load_dotenv()

PORT = int(os.getenv('SERVER_PORT'))
CODEC = os.getenv('CODEC')
SERVER_IP = socket.gethostbyname(socket.gethostname())
logger = get_logger('server', 'logs/server.log')

class Server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, PORT))
    running = False
    client_handlers = []

    def __init__(self):
        self.running = True

    def start(self):
        logger.info(f'[SERVER::{SERVER_IP}] has started.')
        self.server.listen()
        logger.info(f'[SERVER::{SERVER_IP}] is listening.')
        while self.running:
            try:
                conn, addr = self.server.accept()
                self.handle_client(conn, addr)
            except Exception as e:
                logger.exception('\n')

    def handle_client(self, conn, addr):
        client_handler = ClientHandler(conn, addr, self)
        self.client_handlers.append(client_handler)
        client_thread = threading.Thread(target=client_handler.start)
        client_thread.start()

    def remove_client(self, client: ClientHandler):
        for handler in self.client_handlers:
            if handler.addr == client.addr:
                self.client_handlers.remove(client)
                