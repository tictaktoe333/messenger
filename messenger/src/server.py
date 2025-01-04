import copy
import logging
import selectors
import socket
from queue import Queue
from typing import Optional

import yaml

from .client_info import ClientInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sel = selectors.DefaultSelector()


class Server:
    def __init__(self):
        self.server_host: Optional[str] = None
        self.server_port: Optional[int] = None
        self.concurrent_connections: Optional[int] = None
        with open("config.yaml", "r") as f:
            config: dict = yaml.safe_load(f)
            logger.debug("Config loaded:", config)
        self.server_host = config.get("server", {}).get("host", socket.gethostname())
        self.server_port = config.get("server", {}).get("port", 12345)
        self.concurrent_connections = config.get("server", {}).get(
            "concurrent_connections", 10
        )
        self.clients: dict[socket.SocketType, ClientInfo] = dict()
        self.message_queue = Queue()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(self.concurrent_connections)
        logger.info(f"Server listening on {self.server_host}:{self.server_port}")
        sel.register(self.server_socket, selectors.EVENT_READ)
        logger.debug("Selector registered for server socket")

    def send_message_to_client(self, client_socket, message):
        """send a message to a client"""
        try:
            client_socket.send(message.encode("utf-8"))
        except ConnectionResetError:
            print(f"Connection reset by client {client_socket}")
            self.clients.pop(client_socket)
            sel.unregister(client_socket)
            logger.debug(f"Selector unregistered for client socket {client_socket}")
            return None

    def handle_existing_connection(self, client_socket):
        """handle data from an existing client"""
        try:
            data: str = client_socket.recv(1024).decode("utf-8")
        except ConnectionResetError:
            print(f"Connection reset by client {client_socket}")
            self.clients.pop(client_socket)
            sel.unregister(client_socket)
            logger.debug(f"Selector unregistered for client socket {client_socket}")
            return None
        print(f"Received: {data}")
        self.send_message_to_client(client_socket, "Hello from server!")
        header_string_split: list[str] = data.split(":", 3)
        sender_id: str = header_string_split[0]
        receiver_id: str = header_string_split[1]
        only_data: str = header_string_split[3]
        header: str = copy.deepcopy(data).replace(only_data, "")
        self.clients[client_socket].username = sender_id
        if len(data) < 1024:
            self.message_queue.put((sender_id, receiver_id, only_data))
        # TODO: send the message to the receiver
        # TODO: handle the case where the receiver is not connected
        # TODO: handle the case where the message is too long to be sent in one packet

        return None

    def run(self):
        while True:
            # accept an incoming connection
            events = sel.select(timeout=1)
            for key, _mask in events:
                if key.fileobj == self.server_socket:
                    # handle new incoming connections
                    client_socket, addr = self.server_socket.accept()
                    print(f"Accepted connection from {addr}")
                    self.clients[client_socket] = ClientInfo(
                        address=addr, socket=client_socket
                    )
                    sel.register(client_socket, selectors.EVENT_READ)
                    logger.debug(
                        f"Selector registered for client socket {client_socket}"
                    )
                else:
                    self.handle_existing_connection(key.fileobj)
                    logger.debug(f"Handled data from client socket {key.fileobj}")
                while not self.message_queue.empty():
                    sender_id, receiver_id, only_data = self.message_queue.get()
                    for socket, client_info in self.clients.items():
                        print(self.clients.items())
                        if client_info.username == receiver_id:
                            socket.send(only_data.encode("utf-8"))
                        logger.debug(f"Sent message from {sender_id} to {receiver_id}")
            print("Waiting for events...")


# TODO: assign a unique identifier to each client socket and use it for logging and debugging purposes
# TODO: implement routing logic based on the client's username and IP address

if __name__ == "__main__":
    server = Server()
    server.run()
