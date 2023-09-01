import socket
import os
import networking.messages as msg
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
    running = False

    def __init__(self, conn: socket.socket, addr, server):
        self.conn = conn
        self.addr = addr
        self.running = True
        self.server = server
        logger.info(f'[CLIENT::{self.addr[0]}] has connected.')

    def start(self):
        while self.running:
            try:
                msg = self.receive()
                if msg:
                    self.process_message(msg)
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

    def process_message(self, message):
        message = json.loads(message)
        if msg.DISCONNECT in message:
            self.send('OK')
            self.close()
        elif msg.GET_ID in message:
            print(message)
        else:
            print(message)

    def close(self):
        self.running = False
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()
        logger.info(f'[CLIENT::{self.addr[0]}] has disconnected.')
        self.server.remove_client(self)
        