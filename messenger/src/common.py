import os
import queue
from sys import stdin
import threading
import time

from typing import Iterable


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def read_from_input(q: queue.Queue, print_message: str) -> None:
    """reads from input and puts it in a queue"""
    try:
        print(print_message)
        line = stdin.readline().strip()
        q.put(line)
    except KeyboardInterrupt:
        raise KeyboardInterrupt


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
    try:
        while True:
            c: str = ""
            while not q.empty():
                c = q.get()
                yield c
            if c:
                t.join()
                break
            time.sleep(0.1)  # sleep for a short time to avoid busy waiting
    except KeyboardInterrupt:
        t.join()
        raise KeyboardInterrupt


def create_fixed_length_header(header_content: str, header_size: int) -> str:
    """creates a fixed length header with padding"""
    if len(header_content) > header_size:
        raise ValueError(
            f"Header content '{header_content}' exceeds the specified size of {header_size}"
        )
    return header_content.ljust(header_size)
