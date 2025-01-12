import copy
import os
import queue
import re
import signal
from sys import stdin
import sys
import threading
import time

from typing import Iterable

from .screen import Screen


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def signal_handler(signum, frame):
    """signal handler for SIGINT (Ctrl+C)"""
    clear_screen()
    print("Exiting...")
    sys.exit(0)


def setup_signal_handler():
    """sets up signal handler for SIGINT (Ctrl+C)"""
    signal.signal(signal.SIGINT, signal_handler)


def read_from_input(q: queue.Queue, print_message: str, screen: Screen) -> None:
    """reads from input and puts it in a queue"""
    screen.add_command(print_message)
    screen.print_all()
    line = stdin.readline().strip()
    if line == "exit":
        # close down the thread from inside the thread
        sys.exit()

    q.put(line)


def non_blocking_input(print_message: str, screen: Screen) -> Iterable[str]:
    """reads from input and puts it in a queue without blocking"""
    q = queue.Queue()
    t = threading.Thread(
        target=read_from_input,
        args=(q, print_message, screen),
    )
    t.start()
    while True:
        c: str = ""
        while not q.empty():
            c = q.get()
            yield c
        if c:
            t.join()
            break
        if not t.is_alive():  # check if the thread has been stopped by an exit command
            signal.raise_signal(signal.SIGINT)
        time.sleep(0.1)  # sleep for a short time to avoid busy waiting


def create_fixed_length_header(header_content: str, header_size: int) -> str:
    """creates a fixed length header with padding"""
    if len(header_content) > header_size:
        raise ValueError(
            f"Header content '{header_content}' exceeds the specified size of {header_size}"
        )
    return header_content.ljust(header_size)


def check_for_header(packet: bytes) -> bool:
    """checks if a packet contains the expected header"""
    return re.match(b".*:.*:\\d:.*", packet) is not None


def parse_header(packet: bytes):
    """parses the header from a packet"""
    try:
        header_string_split: list[str] = packet.decode("utf-8").split(":", 3)
        # if len(header_string_split) != 4:
        #     self.remove_client("Invalid header format", client_socket)
        #     return None
        sender_id: str = header_string_split[0]
        receiver_id: str = header_string_split[1]
        message_length: int = int(header_string_split[2])
        only_data: str = header_string_split[3]
        header: str = copy.deepcopy(packet.decode("utf-8")).replace(only_data, "")
        return sender_id, receiver_id, message_length, header, only_data
    except IndexError:
        raise ConnectionResetError  # reset if the connection is broken
