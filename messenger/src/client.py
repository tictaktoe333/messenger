import logging
import selectors
import socket
import threading
from typing import Optional
import yaml

from .common import create_fixed_length_header

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Client:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host: Optional[str] = None
        self.server_port: Optional[int] = None
        with open("config.yaml", "r") as config_file:
            config = yaml.safe_load(config_file)
            self.server_host = config.get("server", {}).get(
                "host", socket.gethostbyname()
            )
            self.server_port = config.get("server", {}).get("port", 12345)

        self.server_address = (self.server_host, self.server_port)

    def connect_to_server(self):
        try:
            self.client_socket.connect(self.server_address)
            logger.info(f"Connected to server at {self.server_address}")
        except socket.error as e:
            logger.error(f"Failed to connect: {e}")

    def disconnect_from_server(self):
        try:
            self.client_socket.close()
            logger.info("Disconnected from server")
        except socket.error as e:
            logger.error(f"Failed to disconnect: {e}")

    def send_message_to_user(self, user_id, message):
        try:
            message_length = len(message)
            header_content = f"{user_id}:{message_length}:"
            header = create_fixed_length_header(
                header_content=header_content, header_size=len(header_content)
            )
            self.client_socket.sendall(f"{header}{message}".encode())
            logger.info(f"Sent message to user {user_id}: {message}")
        except socket.error as e:
            logger.error(f"Failed to send message to user: {e}")

    def receive_message(self):
        try:
            data = self.client_socket.recv(1024)
            if not data:
                logger.info("Server disconnected")
                return None
            message = data.decode()
            logger.info(f"Received message: {message}")
            return message
        except socket.error as e:
            logger.error(f"Failed to receive message: {e}")
            return None

    def run(self):
        while True:
            user_id = input("Enter your user ID: ")
            message = input("Enter your message: ")
            self.send_message_to_user(user_id, message)
            received_message = self.receive_message()
            if received_message:
                print(received_message)


if __name__ == "__main__":
    username = "username"  # TODO: Replace with authenticatation system
    password = "password"  # TODO: Replace with authenticatation system
    client = Client(username=username, password=password)
    client.connect_to_server()
    client.run()
