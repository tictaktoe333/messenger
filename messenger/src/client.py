import logging
import selectors
import socket
import threading

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Client:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ("localhost", 55555)

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
