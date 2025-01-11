import datetime
import logging
import socket
from threading import Thread
from typing import Optional
import yaml

from .common import (
    clear_screen,
    create_fixed_length_header,
    non_blocking_input,
    setup_signal_handler,
)
from .screen import Screen

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Client:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.screen = Screen()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host: Optional[str] = None
        self.server_port: Optional[int] = None
        with open("config.yaml", "r") as config_file:
            config = yaml.safe_load(config_file)
            self.server_host = config.get("server", {}).get(
                "host", socket.gethostname()
            )
            self.server_port = config.get("server", {}).get("port", 12345)
            self.bytes_per_packet = config.get("bytes_per_message", 1024)

        self.server_address = (self.server_host, self.server_port)

    def connect_to_server(self) -> None:
        try:
            self.client_socket.connect(self.server_address)
            logger.info(f"Connected to server at {self.server_address}")
            self.client_socket.setblocking(False)
        except socket.error as e:
            logger.error(f"Failed to connect: {e}")

    def disconnect_from_server(self) -> None:
        try:
            self.client_socket.close()
            logger.info("Disconnected from server")
        except socket.error as e:
            logger.error(f"Failed to disconnect: {e}")

    def send_message_to_user(
        self, sender_id: str, receiver_id: str = "", message: str = ""
    ) -> None:
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

    def send_connection_request(self, sender_id: str) -> None:
        try:
            header_content = f"{sender_id}::0:"
            header = create_fixed_length_header(
                header_content=header_content, header_size=len(header_content)
            )
            self.client_socket.send(header.encode())
            logger.info(f"{sender_id} sent connection request to server")
            self.screen.add_message("Connnection request sent to server")
        except socket.error as e:
            logger.error(f"Failed to send message to user: {e}")

    def receive_packet(self) -> bytes:
        # TODO buffer and header
        # if first packet is header, then read rest of packet
        # else read until end of packet
        return self.client_socket.recv(self.bytes_per_packet)

    def receive_message(self) -> None:
        while True:
            try:
                packet = self.receive_packet()  # TODO buffer and header
                if not packet:
                    logger.info("Server disconnected")
                message = packet.decode()
                logger.info(f"Received message: {message}")
                self.screen.add_message(
                    datetime.datetime.now().isoformat() + ": " + message
                )
                if not self.screen.is_empty():
                    clear_screen()
                    self.screen.print_all()
                    continue
            except socket.error as e:
                if e.errno == socket.EWOULDBLOCK or e.errno == socket.EAGAIN:
                    continue
                else:
                    logger.error(f"Failed to receive message: {e}")
                    return None

    def run(self):
        user_id: str = ""
        for c in non_blocking_input(
            print_message="Enter user ID to send message to: ", screen=self.screen
        ):
            user_id += c
        while True:
            message: str = ""
            for c in non_blocking_input(
                print_message="Enter message to send: ", screen=self.screen
            ):
                message += c
            if message:
                self.send_message_to_user(
                    sender_id=self.username, receiver_id=user_id, message=message
                )


if __name__ == "__main__":
    setup_signal_handler()
    username = input("Enter your username: ")
    password = "password"  # TODO: Replace with authentication system
    client = Client(username=username, password=password)
    client.connect_to_server()
    client.send_message_to_user(sender_id=username)  # to connect and register user
    receive_thread: Thread = Thread(target=client.receive_message, daemon=True)
    receive_thread.start()
    run_thread: Thread = Thread(target=client.run, daemon=True)
    run_thread.start()
    receive_thread.join()
    run_thread.join()
