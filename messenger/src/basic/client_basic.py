import socket

HEADER_SIZE = 10

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostname(), 12345))

while True:
    full_msg = ""
    new_message = True
    while True:
        msg = client_socket.recv(16)
        if new_message:
            msglen = int(msg[:HEADER_SIZE])
            print(f"new message len: {msg[:HEADER_SIZE]}")
            new_message = False
        full_msg += msg.decode("utf-8")
        if len(full_msg) - HEADER_SIZE == msglen:
            print("full msg received")
            print(full_msg[HEADER_SIZE:])
            new_message = True
            full_msg = ""
