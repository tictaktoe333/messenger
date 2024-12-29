import logging
import selectors
import socket
import threading
import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Client:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = "localhost"
        self.server_port = 8080
        with open("config.yaml", "r") as config_file:
            config = yaml.safe_load(config_file)
            self.server_host = config.get("server", {}).get("host", "localhost")
            self.server_port = config.get("server", {}).get("port", 8080)

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

    def send_message_to_server(self, message):
        try:
            self.client_socket.sendall(message.encode())
            logger.info(f"Sent message: {message}")
        except socket.error as e:
            logger.error(f"Failed to send message: {e}")

    def send_message_to_user(self, user_id, message):
        try:
            self.client_socket.sendall(f"{user_id}:{message}".encode())
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
    username = "username"  # TODO: Replace with your authenticatation system
    password = "password"  # TODO: Replace with your authenticatation system
    client = Client(username=username, password=password)
    client.connect_to_server()
    client.run()
