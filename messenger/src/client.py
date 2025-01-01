import logging
import socket
import sys
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
                "host", socket.gethostname()
            )
            self.server_port = config.get("server", {}).get("port", 12345)

        self.server_address = (self.server_host, self.server_port)

    def connect_to_server(self):
        try:
            self.client_socket.connect(self.server_address)
            logger.info(f"Connected to server at {self.server_address}")
            self.client_socket.setblocking(False)
        except socket.error as e:
            logger.error(f"Failed to connect: {e}")

    def disconnect_from_server(self):
        try:
            self.client_socket.close()
            logger.info("Disconnected from server")
        except socket.error as e:
            logger.error(f"Failed to disconnect: {e}")

    def send_message_to_user(self, sender_id: str, receiver_id: str, message: str):
        try:
            message_length = len(message)
            header_content = f"{sender_id}:{receiver_id}:{message_length}:"
            header = create_fixed_length_header(
                header_content=header_content, header_size=len(header_content)
            )
            self.client_socket.send(f"{header}{message}".encode())
            logger.info(f"{sender_id} sent message to user {receiver_id}: {message}")
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
            if e.errno == socket.EWOULDBLOCK or e.errno == socket.EAGAIN:
                logger.info("Server is busy")
                return None
            else:
                logger.error(f"Failed to receive message: {e}")
                return None

    def run(self):
        while True:
            try:
                user_id = input("Send message to user: ")
                message = input("Enter your message: ")
                self.send_message_to_user(
                    sender_id=self.username, receiver_id=user_id, message=message
                )
                received_message = self.receive_message()
                if received_message:
                    print(received_message)
            except KeyboardInterrupt or SystemExit:
                self.client_socket.close()
                logger.info("Exiting program")
                sys.exit(130)


if __name__ == "__main__":
    username = input("Enter your username: ")
    password = "password"  # TODO: Replace with authenticatation system
    client = Client(username=username, password=password)
    client.connect_to_server()
    client.run()
