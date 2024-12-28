import logging
import selectors
import socket
import yaml


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sel = selectors.DefaultSelector()


class Server:
    def __init__(self):
        self.host = None
        self.port = None
        self.concurrent_connections = None
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            logger.debug("Config loaded:", config)
        self.host = config.get("server", {}).get("host", "localhost")
        self.port = config.get("server", {}).get("port", 8080)
        self.concurrent_connections = config.get("server", {}).get(
            "concurrent_connections", 10
        )
        self.clients = set()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.concurrent_connections)
        logger.info(f"Server listening on {self.host}:{self.port}")
        sel.register(self.server_socket, selectors.EVENT_READ)
