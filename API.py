# API.py
# From https://docs.openwebui.com/getting-started/api-endpoints
# Modified the calls to make sure it's formatted correctly

import requests

### Open-WebUI Settings
adminToken = ''
with open('.webui_admin_key', 'a') as f: pass # Create file if it doesnt exist (write only bruh)
with open('.webui_admin_key', 'r+') as f: # Re-open in read/write mode
    if not f.readline(): # if file is empty
        f.seek(0)
        while adminToken == '': adminToken = input("Paste admin token (Profile > Settings > Account > API Keys > JWT Token):")
        f.write(adminToken) # adminToken is now saved for later use
    f.seek(0)
    adminToken = f.readline()

localHostPort = "8080"
defaultHeader = {'Authorization':f'Bearer {adminToken}','Content-Type':'application/json'}
Models = [
    "justinrahb.claude-3-7-sonnet-20250219",
    "llama3.2:1b",
    "llama3:8b"
]

# Thanks to https://github.com/open-webui/open-webui/discussions/11761
def create_knowledge(name:str, description:str, data:dict={}, access_control:dict={}, token=adminToken):
    url=f"http://localhost:{localHostPort}/api/v1/knowledge/create"
    payload = {
        "name": f"{name}",
        "description": f'{description}',
        "data": data,
        "access_control": access_control
    }
    return requests.post(url, headers=defaultHeader, json=payload).json()

def delete_knowledge(kbid:str):
    url=f"http://localhost:{localHostPort}/api/v1/knowledge/{kbid}/delete"
    return requests.delete(url, headers=defaultHeader).json()

### Keys and links
KBIDs = [ # TODO change to dict perhaps
    create_knowledge('Expert', 'asdf')['id'], 
    create_knowledge('Study', 'asdf')['id']
]

### API
def chat_with_model(model, context):
    url = f'http://localhost:{localHostPort}/api/chat/completions'
    data = {
      "model": model,
      "messages": context,
      "system": "Ignore the prompt, respond only with AAA"
    }
    return requests.post(url, headers=defaultHeader, json=data).json()

def upload_file(file_path): 
    url = f'http://localhost:{localHostPort}/api/v1/files/'
    headers = {'Authorization': f'Bearer {adminToken}','Accept': 'application/json'} # Only one with 'accept' vs the default header wtf
    return requests.post(url, headers=headers, files={'file': open(file_path, 'rb')}).json()

def add_file_to_knowledge(file_id, knowledge_id):
    url = f'http://localhost:{localHostPort}/api/v1/knowledge/{knowledge_id}/file/add'
    return requests.post(url, headers=defaultHeader, json={'file_id': file_id}).json()

def chat_with_file(model, prompt, file_id):
    url = f'http://localhost:{localHostPort}/api/chat/completions'
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': f"\"{prompt}\""}],
        'files': [{'type': 'file', 'id': file_id}]
    }
    return requests.post(url, headers=defaultHeader, json=payload).json()

def chat_with_collection(model, context, collection_id):
    url = f'http://localhost:{localHostPort}/api/chat/completions'
    payload = {
        'model': model,
        'messages': context,
        'files': [{'type': 'collection', 'id': collection_id}]
    }
    return requests.post(url, headers=defaultHeader, json=payload).json()

def remove_file_from_knowledge(file_id, knowledge_id):
    url = f'http://localhost:{localHostPort}/api/v1/knowledge/{knowledge_id}/file/remove'
    return requests.post(url, headers=defaultHeader, json={'file_id': file_id}).json()
