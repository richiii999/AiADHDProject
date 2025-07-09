# API.py
# From https://docs.openwebui.com/getting-started/api-endpoints
# Modified the calls to make sure it's formatted correctly

import requests

### Open-WebUI Settings
localHostPort = "8080"
adminToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImU1MTJhMjRjLTQ5YmMtNDFkYS1hMDQ2LTQ1MzFjNGQ1MGY1OSJ9.hS94_5e9x9G8sVmZbqmS2WFX7iB09ylCHWkbOI5bQu4'
defaultHeader = {'Authorization':f'Bearer {adminToken}','Content-Type':'application/json'}
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
    
    response = requests.post(url, headers=defaultHeader, json=payload)
    return response.json()

def delete_knowledge(kbid:str):
    url=f"http://localhost:{localHostPort}/api/v1/knowledge/{kbid}/delete"
    return requests.delete(url, headers=defaultHeader).json()

### Keys and links
KBIDs = [ # TODO change to dict perhaps
    create_knowledge('Expert', 'asdf')['id'], 
    create_knowledge('Study', 'asdf')['id']
]
print(KBIDs)

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
