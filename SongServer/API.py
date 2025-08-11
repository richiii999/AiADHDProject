### API.py
# Formats API requests to the OpenWebUI docker image

import requests
import subprocess
import socket

SERVER_HOST = "192.168.0.200"
# 172.17.0.2    - Docker IP addr, doesnt work
# 192.168.0.200 - ip addr, works locally
# localhost     - Works locally ofc

SERVER_PORT = 3001
# 3000 - OpenWebUI Docker port
# 8080 - OpenWebUI port (not docker)

# TCP Funcs
def Send(socket, msg): # Sending func
    socket[0].send(msg.encode())
    print(f"-> {socket[1][0]}: {msg}")

def Recieve(socket) -> str: # Recieving func
    data = socket[0].recv(1024).decode()
    print(f"<- {socket[1][0]}: {data}")
    return data

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_HOST, SERVER_PORT))
print(f"TCP Listening on {SERVER_HOST}:{SERVER_PORT}...")

models = [] + subprocess.check_output("ollama list | grep -v NAME | awk '{print $1}'", shell=True).decode('utf-8').split('\n')[:-1]
modelNum = -1 # Set by user on startup

APIKey = ""
with open('.webui_admin_key', 'a') as f: pass # Create file if it doesnt exist (write only bruh)
with open('.webui_admin_key', 'r+') as f: # Re-open in read/write mode
    if not f.readline(): # if file is empty
        f.seek(0)
        while APIKey == '': APIKey = input("Paste admin token (Profile > Settings > Account > API Keys > JWT Token):")
        f.write(APIKey) # adminToken is now saved for later use
    f.seek(0)
    APIKey = f.readline()

defaultHeader = {'Authorization':f'Bearer {APIKey}','Content-Type':'application/json'}

def UserInput(inputPrompt, validinput=None) -> str: # User input verification
    i = input(inputPrompt)
    while i not in validinput:
        print("Invalid input, try again")
        i = input(inputPrompt)
    return i

def sanitize(s) -> str: # Sanitize input
    s.replace('"','')
    s.replace("'",'')
    return s

def chat_with_model(prompt) -> str:
    url = f'http://{SERVER_HOST}:{3000}/api/chat/completions'
    print(prompt)
    data = {
      "model": models[modelNum],
      "messages": [{"role":"user","content":sanitize(prompt)}]
    }
    return requests.post(url, headers=defaultHeader, json=data).json()['choices'][0]['message']['content']

modelNum = int(UserInput("Please select a model # from the list:\n" + '\n'.join(['{}: {}'.format(i,val) for i, val in (enumerate(models))]) + "\n>", [str(i) for i in range(len(models))]))

# interactive mode
# try:
#     while True: print(chat_with_model(models[modelNum],input(f"{models[modelNum]}>")))
# except KeyboardInterrupt: print("\nExiting...\n")

# TCP Socket mode
while True:
    print("listening...")
    server.listen()
    client = server.accept() # recieve (conn, addr) from client
    
    MSG = Recieve(client) # Recieve MSG
    print("msg recieved")

    response = chat_with_model(MSG)
    print("response = " + response)
    Send(client, response)
    print("response sent")
