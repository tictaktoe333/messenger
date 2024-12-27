import logging
import selectors
import socket
import threading

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sel = selectors.DefaultSelector()


class Server:
    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = port
        self.clients = set()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        logger.info(f"Server listening on {self.host}:{self.port}")
        sel.register(self.server_socket, selectors.EVENT_READ)
