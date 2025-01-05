import os
import queue
import signal
from sys import stdin
import sys
import threading
import time

from typing import Iterable


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


def read_from_input(q: queue.Queue, print_message: str) -> None:
    """reads from input and puts it in a queue"""
    print(print_message)
    line = stdin.readline().strip()
    if line == "exit":
        # close down the thread from inside the thread
        sys.exit()

    q.put(line)


def non_blocking_input(print_message: str) -> Iterable[str]:
    """reads from input and puts it in a queue without blocking"""
    q = queue.Queue()
    t = threading.Thread(
        target=read_from_input,
        args=(
            q,
            print_message,
        ),
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
            raise KeyboardInterrupt
        time.sleep(0.1)  # sleep for a short time to avoid busy waiting


def create_fixed_length_header(header_content: str, header_size: int) -> str:
    """creates a fixed length header with padding"""
    if len(header_content) > header_size:
        raise ValueError(
            f"Header content '{header_content}' exceeds the specified size of {header_size}"
        )
    return header_content.ljust(header_size)
