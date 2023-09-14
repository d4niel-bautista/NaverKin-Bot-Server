import socket
import threading
import os
from .client_handler import ClientHandler
from .service import Service
from database.data_access import DataAccess
from utils import get_logger, fetch_server_ip
from dotenv import load_dotenv
load_dotenv()

PORT = int(os.getenv('SERVER_PORT'))
CODEC = os.getenv('CODEC')
SERVER_IP = fetch_server_ip()
logger = get_logger('server', 'logs/server.log')

class Server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, PORT))
    running = False
    client_handlers = []

    def __init__(self):
        self.running = True

    def start(self):
        print('SERVER HAS STARTED')
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
        print(f"{addr[0]} HAS CONNECTED")
        data_access = DataAccess()
        service = Service(data_access)
        client_handler = ClientHandler(conn, addr, self, service)
        self.client_handlers.append(client_handler)
        client_thread = threading.Thread(target=client_handler.start)
        client_thread.start()

    def remove_client(self, client: ClientHandler):
        for handler in self.client_handlers:
            if handler.addr == client.addr:
                print(f"{client.addr[0]} HAS DISCONNECTED")
                self.client_handlers.remove(client)
                