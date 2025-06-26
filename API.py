# API.py
# From https://docs.openwebui.com/getting-started/api-endpoints
# Slightly modified the calls to make sure it's formatted correctly

import requests

### Open-WebUI Settings
localHostPort = "8080"
model = "llama3:8b" # Default: "llama3.2:latest"
#base = "llama3.2:1b"

### Keys and links
kb_id = "4a1f7b67-261b-4588-bae8-1ee784699b8a" # 'asdf' KB on webui
adminToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQ4NWJmMzUwLWI0YmQtNDNlMC04NTkxLTBhYTJlZDc0M2M5YyJ9.JSOQTr-v0FfcOiFrrZ3K7B21qP3DwzHtNHbzaFcYWZo'
def chat_with_model(prompt, token=adminToken):
    url = f'http://localhost:{localHostPort}/api/chat/completions'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
      "model": model,
      "messages": [
        {
          "role": "user",
          "content": f"\"{prompt}\""
        }
      ]
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

def add_file_to_knowledge(file_id, knowledge_id = kb_id, token=adminToken):
    url = f'http://localhost:{localHostPort}/api/v1/knowledge/{knowledge_id}/file/add'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {'file_id': file_id}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def chat_with_file(prompt, file_id, token=adminToken):
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

def chat_with_collection(prompt, collection_id, token=adminToken):
    url = f'http://localhost:{localHostPort}/api/chat/completions'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': f"\"{prompt}\""}],
        'files': [{'type': 'collection', 'id': collection_id}]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def remove_file_from_knowledge(knowledge_id, file_id):
    url = f'http://localhost:{localHostPort}/api/v1/knowledge/{knowledge_id}/file/remove'
    headers = {
        'Authorization': f'Bearer {adminToken}',
        'Content-Type': 'application/json'
    }
    data = {'file_id': file_id}
    response = requests.post(url, headers=headers, json=data)
    return response.json()
