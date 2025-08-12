### SongClient.py
# Gives a user-interface to talk to SongServer. stdin is sent to the server, the response is printed to stdout

import socket

# Client Networking
default_IP = '192.168.0.200'

SERVER_HOST = ''
SERVER_PORT = 3001

while not SERVER_HOST:
    try: 
        IP = input("Server IP (Default 192.168.0.200): ")
        if not IP: IP = default_IP
        SERVER_HOST = socket.gethostbyname(IP)
    except socket.error: 
        print("Couldn't connect, try again")
        # TODO: Perhaps when client closes (or connection ends for any reason), go back to top ^
        # TODO: Invalid but properly formatted IPs (ex. 123.123.123.123) infinite execution, need to prevent such connections.

# TCP Funcs
def Send(socket, msg): socket.sendall(msg.encode())
def Recieve(socket) -> str: return socket.recv(1024).decode()

while True: # Main Loop
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((SERVER_HOST, SERVER_PORT)) # socket for server

    MSG = input("Prompt>")
    Send(server, MSG)
    print("Server says:" + Recieve(server))
