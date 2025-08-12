### API.py
# Formats API requests to the OpenWebUI docker image

import requests
import subprocess
import socket

def MyIP(): # From https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib#166589
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try: # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception: IP = '127.0.0.1'
    finally: s.close()
    return IP

# BUG: Newlines as part of the recieved msg seem to cause issues
# BUG: There is a max msg length, setting the .recv() to greater than 1024 doesnt increase this. It's about 10 full lines of text on the terminal
    # When the msg is very long, it seems to recieve 2 pkts as one prompt, which is fine, but still not enough for very long msg (>2048)

SERVER_HOST = MyIP() # Default 192.168.0.200
# 172.17.0.2    - Docker IP addr, doesnt work
# 192.168.0.200 - .100 other pc

SERVER_PORT = 3001
DockerPort = 3000
# 8080 - OpenWebUI port (not docker)

def Send(socket, msg): socket[0].send(msg.encode())
def Recieve(socket) -> str: return socket[0].recv(8192).decode() # default 1024, changed to 8192 but it seems the max incoming is 4095

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reusable ports, to not force a 30s wait for the port to clear
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

def chat_with_model(prompt) -> str:
    url = f'http://{SERVER_HOST}:{DockerPort}/api/chat/completions'
    data = {
      "model": models[modelNum],
      "messages": [{"role":"user","content":prompt}]
    }
    return requests.post(url, headers=defaultHeader, json=data).json()['choices'][0]['message']['content']

modelNum = int(UserInput("Please select a model # from the list:\n" + '\n'.join(['{}: {}'.format(i,val) for i, val in (enumerate(models))]) + "\n>", [str(i) for i in range(len(models))]))

try: 
    while True: # Main Loop
        server.listen()
        client = server.accept() # recieve (conn, addr) from client
        
        MSG = Recieve(client) 
        print(f"<- {client[1][0]} len {len(MSG)}: {MSG}")

        response = chat_with_model(MSG)
        
        Send(client, response)
        print(f"-> {client[1][0]}: {response}")
except KeyboardInterrupt: 
    server.close()
    print("Exiting...")