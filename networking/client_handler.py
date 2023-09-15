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
    def __init__(self, conn: socket.socket, addr, server, service):
        self.conn = conn
        self.addr = addr
        self.running = True
        self.server = server
        self.service = service
        logger.info(f'[CLIENT::{self.addr[0]}] has connected.')
        self.client_username = ''
        self.service.set_clienthandler(self)

    def start(self):
        while self.running:
            try:
                msg = self.receive()
                if msg:
                    self.process_request(msg)
            except:
                logger.exception('\n')
                self.close()
    
    def send(self, message):
        self.conn.send(json.dumps(message).encode(CODEC))
    
    def broadcast_message(self, message, exclude=''):
        self.server.broadcast_message(message, exclude)

    def send_to_target(self, message, target):
        self.server.send_to_target(message, target)

    def receive(self):
        message = self.conn.recv(HEADER_LEN).decode(CODEC)
        return message

    def process_request(self, request):
        request = json.loads(request)
        if request['message'] == 'DISCONNECT':
            self.send('OK')
            self.close()
        elif request['message'] == 'GET_ACCOUNT':
            response = self.service.process_request(request)
            if type(response) is dict:
                self.client_username = response['username']
            self.send(response)
        else:
            response = self.service.process_request(request)
            self.send(response)

    def close(self):
        self.running = False
        self.service.update_account(username=self.client_username, status=0)
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()
        logger.info(f'[CLIENT::{self.addr[0]}] has disconnected.')
        self.server.remove_client(self)