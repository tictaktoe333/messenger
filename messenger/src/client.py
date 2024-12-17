# Client for the server

import socket
import threading

# client configuration
host = '192.168.2.111'
port = 55555

# create a socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

# receive messages from the server
def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            print("An error occurred!")
            client.close()
            break

# send messages to the server
def write():
    while True:
        message = f'{nickname}: {input("")}'
        client.send(message.encode('ascii'))

# set nickname
nickname = input("Choose a nickname: ")

# start threads for receiving and writing messages
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)

write_thread.start()
