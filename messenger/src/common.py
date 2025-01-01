import queue
import sys
import threading
import time


# function that reads from stdin and puts it in a queue
def read_from_stdin(q: queue.Queue):
    while True:
        q.put(sys.stdin.read(1))


# non-blocking input function that reads from stdin without blocking
def non_blocking_input(print_message: str):
    print(print_message)
    q = queue.Queue()
    t = threading.Thread(target=read_from_stdin, args=(q,))
    t.start()
    while True:
        message: str = ""
        while not q.empty():
            message += q.get()
        if message != "" and message.endswith("\n"):
            q.queue.clear()
            return message.strip("\n")


def create_fixed_length_header(header_content: str, header_size: int) -> str:
    if len(header_content) > header_size:
        raise ValueError(
            f"Header content '{header_content}' exceeds the specified size of {header_size}"
        )
    return header_content.ljust(header_size)
