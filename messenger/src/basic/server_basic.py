import socket

HEADER_SIZE = 10


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((socket.gethostname(), 12345))
server_socket.listen(5)

msg = "Hello, client!"
msg = f"{len(msg):<{HEADER_SIZE}}" + msg

while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr} has been established")
    client_socket.send(bytes(msg, "utf-8"))
