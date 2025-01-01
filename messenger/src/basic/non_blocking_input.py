import sys
import threading
import time
import queue


# non-blocking input function that reads from stdin without blocking
def non_blocking_input():
    # create a queue to hold the input
    q = queue.Queue()
    # start a thread to read from stdin and put it in the queue
    t = threading.Thread(target=read_from_stdin, args=(q,))
    t.start()
    # wait for the input to be available in the queue
    while True:
        if not q.empty():
            print(q.get())
        time.sleep(0.1)


# function that reads from stdin and puts it in a queue
def read_from_stdin(q):
    while True:
        line = sys.stdin.readline()
        if line == "":
            break
        q.put(line)
        time.sleep(0.1)


if __name__ == "__main__":
    non_blocking_input()
