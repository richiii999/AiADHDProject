### API.py
# Formats API requests to the OpenWebUI docker image

import requests
import subprocess
import socket

# BUG: Newlines as part of the recieved msg seem to cause issues
# BUG: There is a max msg length, setting the .recv() to greater than 1024 doesnt increase this. It's about 10 full lines of text on the terminal
    # When the msg is very long, it seems to recieve 2 pkts as one prompt, which is fine, but still not enough for very long msg (>2048)

SERVER_HOST = "192.168.0.200"
# 172.17.0.2    - Docker IP addr, doesnt work
# 192.168.0.200 - ip addr, works locally
# localhost     - Works locally ofc

SERVER_PORT = 3001
DockerPort = 3000
# 3000 - Docker port for the OpenWebUI container
# 8080 - OpenWebUI port (not docker)

def Send(socket, msg): socket[0].send(msg.encode())
def Recieve(socket) -> str: 
    data = ''
    while True: # default chunksize 1024, changed to 2048 but it seems the max incoming is 1448
        print("before rec")
        datachunk = socket[0].recv(1024).decode()  # reads data chunk from the socket in batches using method recv() until it returns an empty string
        print("-> " + datachunk)
        if not datachunk: break  # no more data coming in, so break out of the while loop
        data += datachunk  # add chunk to your already collected data
    return data

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reusable ports, to make restarting not force a 30s wait for the port to clear
server.bind((SERVER_HOST, SERVER_PORT))
print(f"TCP Listening on {SERVER_HOST}:{SERVER_PORT}")

models = [] + subprocess.check_output("ollama list | grep -v NAME | awk '{print $1}'", shell=True).decode('utf-8').split('\n')[:-1]

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
    url = f'http://{SERVER_HOST}:{DockerPort}/api/chat/completions'
    print(prompt)
    data = {
      "model": models[modelNum],
      "messages": [{"role":"user","content":sanitize(prompt)}]
    }
    return requests.post(url, headers=defaultHeader, json=data).json()['choices'][0]['message']['content']

modelNum = int(UserInput("Please select a model # from the list:\n" + '\n'.join(['{}: {}'.format(i,val) for i, val in (enumerate(models))]) + "\n>", [str(i) for i in range(len(models))]))

while True: # Main Loop
    server.listen()
    client = server.accept() # recieve (conn, addr) from client
    
    MSG = Recieve(client) 
    print(f"<- {client[1][0]}: {MSG}")

    response = chat_with_model(MSG)
    
    Send(client, response)
    print(f"-> {client[1][0]}: {response}")

server.bind
