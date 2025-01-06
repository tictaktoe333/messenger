import copy
import logging
import selectors
import socket
from queue import Queue

import yaml

from messenger.src.common import setup_signal_handler

from .client_info import ClientInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Server:
    def __init__(self):
        self.sel = selectors.DefaultSelector()
        with open("config.yaml", "r") as f:
            config: dict = yaml.safe_load(f)
            logger.debug("Config loaded:", config)
        self.server_host: str = config.get("server", {}).get(
            "host", socket.gethostname()
        )
        self.server_port: int = config.get("server", {}).get("port", 12345)
        self.concurrent_connections: int = config.get("server", {}).get(
            "concurrent_connections", 10
        )
        self.bytes_per_message: int = config.get("server", {}).get(
            "bytes_per_message", 1024
        )
        self.clients: dict[socket.SocketType, ClientInfo] = dict()
        self.message_queue: Queue[tuple[str, str, str]] = Queue()
        self.server_socket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(self.concurrent_connections)
        logger.info(f"Server listening on {self.server_host}:{self.server_port}")
        self.sel.register(self.server_socket, selectors.EVENT_READ)
        logger.debug("Selector registered for server socket")

    def remove_client(self, issue: str, client_socket):
        """remove a client from the list of clients"""
        print(f"{issue}, removing {client_socket}")
        self.clients.pop(client_socket)
        self.sel.unregister(client_socket)
        logger.debug(f"Selector unregistered for client socket {client_socket}")

    def send_message_to_client(self, client_socket, message):
        """send a message to a client"""
        try:
            client_socket.send(message.encode("utf-8"))
        except ConnectionResetError:
            self.remove_client("Connection reset by client", client_socket)
        except BrokenPipeError:
            self.remove_client("Broken pipe by client", client_socket)

    def handle_existing_connection(self, client_socket):
        """handle data from an existing client"""
        try:
            data: str = client_socket.recv(self.bytes_per_message).decode("utf-8")
            header_string_split: list[str] = data.split(":", 3)
            if len(header_string_split) != 4:
                self.remove_client("Invalid header format", client_socket)
                return None
            sender_id: str = header_string_split[0]
            receiver_id: str = header_string_split[1]
            only_data: str = header_string_split[3]
            header: str = copy.deepcopy(data).replace(only_data, "")
            self.clients[client_socket].username = sender_id
            print(f"Received: {data}")
            # self.send_message_to_client(client_socket, "Hello from server!")
            if len(data) < self.bytes_per_message:
                self.message_queue.put((sender_id, receiver_id, only_data))
        except ConnectionResetError:
            self.remove_client("Connection reset by peer", client_socket)
            return None

    def events_handler(self, events):
        for key, _mask in events:
            if key.fileobj == self.server_socket:
                # handle new incoming connections
                client_socket, addr = self.server_socket.accept()
                print(f"Accepted connection from {addr}")
                self.clients[client_socket] = ClientInfo(
                    address=addr, socket=client_socket
                )
                self.sel.register(client_socket, selectors.EVENT_READ)
                logger.debug(f"Selector registered for client socket {client_socket}")
                self.send_message_to_client(client_socket, "connected!")
            elif key.fileobj in self.clients:
                self.handle_existing_connection(client_socket=key.fileobj)
                logger.debug(f"Handled data from client socket {key.fileobj}")
            while not self.message_queue.empty():
                sender_id, receiver_id, only_data = self.message_queue.get()
                for socket, client_info in self.clients.items():
                    if client_info.username == receiver_id:
                        socket.send((sender_id + ": " + only_data).encode("utf-8"))
                    logger.debug(f"Sent message from {sender_id} to {receiver_id}")

    def run(self):
        while True:
            # accept an incoming connection
            try:
                events = self.sel.select(timeout=1)
                self.events_handler(events)
                print("Waiting for events...")
            except KeyboardInterrupt:
                break
        self.sel.close()


if __name__ == "__main__":
    setup_signal_handler()
    server = Server()
    server.run()
