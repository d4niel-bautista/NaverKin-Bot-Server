import socket
import os
import json
from utils import get_logger
from dotenv import load_dotenv
load_dotenv()

CODEC = os.getenv('CODEC')
HEADER_LEN = int(os.getenv('HEADER_LEN'))
logger = get_logger('server', 'logs/server.log')

class ClientHandler():
    addr = None
    conn = None
    server = None
    service = None
    running = False

    def __init__(self, conn: socket.socket, addr, server, service):
        self.conn = conn
        self.addr = addr
        self.running = True
        self.server = server
        self.service = service
        logger.info(f'[CLIENT::{self.addr[0]}] has connected.')

    def start(self):
        while self.running:
            try:
                msg = self.receive()
                if msg:
                    self.process_request(msg)
            except ConnectionError as e:
                logger.error(e)
                self.close()
            except:
                logger.exception('\n')
    
    def send(self, message):
        self.conn.send(json.dumps(message).encode(CODEC))

    def receive(self):
        message = self.conn.recv(HEADER_LEN).decode(CODEC)
        return message

    def process_request(self, request):
        request = json.loads(request)
        if request['message'] == 'DISCONNECT':
            self.send('OK')
            self.close()
        else:
            response = self.service.process_request(request)
            self.send(response)

    def close(self):
        self.running = False
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()
        logger.info(f'[CLIENT::{self.addr[0]}] has disconnected.')
        self.server.remove_client(self)
        