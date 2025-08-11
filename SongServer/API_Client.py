### API_Client.py

import socket

# Client Networking
SERVER_HOST = ''
while SERVER_HOST == '':
    try: SERVER_HOST = socket.gethostbyname(input("Server IP: "))
    except socket.error: print ("Couldn't connect, try again")
SERVER_PORT = 3001

# TCP Funcs
def Send(socket, msg):
    socket.sendall(msg.encode())

def Recieve(socket) -> str:
    msg = socket.recv(1024).decode()
    print(f"Server: {msg}")
    return msg

while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT)) # Client Socket

    MSG = input("Prompt> ")

    Send(client, MSG)
    print("msg sent")
    Recieve(client)
    print("response recieved")
