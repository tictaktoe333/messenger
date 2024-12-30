import logging
import selectors
import socket
from typing import Optional

import yaml

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
        self.server_host = config.get("server", {}).get(
            "host", socket.getsockethostname()
        )
        self.server_port = config.get("server", {}).get("port", 12345)
        self.concurrent_connections = config.get("server", {}).get(
            "concurrent_connections", 10
        )
        self.clients = set()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(self.concurrent_connections)
        logger.info(f"Server listening on {self.server_host}:{self.server_port}")
        sel.register(self.server_socket, selectors.EVENT_READ)
        logger.debug("Selector registered for server socket")

    def run(self):
        while True:
            # accept an incoming connection
            client_socket, addr = self.server_socket.accept()
            print(f"Connected by {addr}")
            # receive data from the client
            data = client_socket.recv(1024).decode("utf-8")
            print(f"Received: {data}")
            # send a response back to the client
            response = "Hello, client!"
            client_socket.sendall(response.encode("utf-8"))
            # register the client socket with the selector for read events
            sel.register(client_socket, selectors.EVENT_READ)
            logger.debug(f"Selector registered for client socket {client_socket}")
            # wait for events on the selector
            events = sel.select(timeout=1)
            for key, mask in events:
                if key.fileobj == self.server_socket:
                    # handle new incoming connections
                    pass
                elif key.fileobj == client_socket:
                    # handle data received from the client
                    data = client_socket.recv(1024).decode("utf-8")
                    print(f"Received: {data}")
                    # send a response back to the client
                    response = "Hello, client!"
                    client_socket.sendall(response.encode("utf-8"))
                else:
                    # handle other events (e.g., write events)
                    pass
            # close the connection with the client
            client_socket.close()


if __name__ == "__main__":
    server = Server()
    server.run()
