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
            # close the connection with the client
            client_socket.close()


if __name__ == "__main__":
    server = Server()
    server.run()
