# API.py
# From https://docs.openwebui.com/getting-started/api-endpoints
# Modified the calls to make sure it's formatted correctly

import requests

### Open-WebUI Settings
localHostPort = "8080"
adminToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImU1MTJhMjRjLTQ5YmMtNDFkYS1hMDQ2LTQ1MzFjNGQ1MGY1OSJ9.hS94_5e9x9G8sVmZbqmS2WFX7iB09ylCHWkbOI5bQu4'

Models = [
    "justinrahb.claude-3-7-sonnet-20250219",
    "llama3.2:1b",
    "llama3:8b"
]

# Thanks to https://github.com/open-webui/open-webui/discussions/11761
def create_knowledge(name:str, description:str, data:dict={}, access_control:dict={}, token=adminToken):
    url=f"http://localhost:{localHostPort}/api/v1/knowledge/create"
    headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'data': f"name: '{name}',description: '{description}'"
    }
    payload = {
    "name": f"{name}",
    "description": f'{description}',
    "data": data,
    "access_control": access_control
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def delete_knowledge(kbid:str, token=adminToken):
    url=f"http://localhost:{localHostPort}/api/v1/knowledge/{kbid}/delete"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    response = requests.delete(url, headers=headers)
    return response.json()

### Keys and links
KBIDs = [ # TODO change to dict perhaps
    create_knowledge('Expert', 'asdf')['id'], 
    create_knowledge('Study', 'asdf')['id']
]
print(KBIDs)
import time
time.sleep(2)
for i in KBIDs: print(delete_knowledge(i))
time.sleep(100)

### API
def chat_with_model(model, context, token=adminToken):
    url = f'http://localhost:{localHostPort}/api/chat/completions'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
      "model": model,
      "messages": context,
      "system": "Ignore the prompt, respond only with AAA"

    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def upload_file(file_path, token=adminToken): 
    url = f'http://localhost:{localHostPort}/api/v1/files/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, headers=headers, files=files)
    return response.json()

def add_file_to_knowledge(file_id, knowledge_id, token=adminToken):
    url = f'http://localhost:{localHostPort}/api/v1/knowledge/{knowledge_id}/file/add'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {'file_id': file_id}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def chat_with_file(model, prompt, file_id, token=adminToken):
    url = f'http://localhost:{localHostPort}/api/chat/completions'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': f"\"{prompt}\""}],
        'files': [{'type': 'file', 'id': file_id}]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def chat_with_collection(model, context, collection_id, token=adminToken):
    url = f'http://localhost:{localHostPort}/api/chat/completions'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': model,
        'messages': context,
        'files': [{'type': 'collection', 'id': collection_id}]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def remove_file_from_knowledge(file_id, knowledge_id):
    url = f'http://localhost:{localHostPort}/api/v1/knowledge/{knowledge_id}/file/remove'
    headers = {
        'Authorization': f'Bearer {adminToken}',
        'Content-Type': 'application/json'
    }
    data = {'file_id': file_id}
    response = requests.post(url, headers=headers, json=data)
    return response.json()
