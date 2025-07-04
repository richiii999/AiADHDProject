import API
import subprocess

prompt = "test"
context = [{"role":"user", "content":prompt.replace('\"','')}]
print(context)
subprocess.run(f'curl http://localhost:11434/api/chat/completions -d {{ "model": "{API.model}", "messages": {context}, "stream":false }}', shell=True)

adminToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxOTBjYTQ1LTgxNzgtNGQ4NC1hYTAwLTNmYTQ4MWFiM2MwMiJ9.z2lI5wfu3uvuZ4ImS-QI3aEceiu1n-NhsIS2Yn-FfPE'




curl http://localhost:11434/api/generate 
-H "Authorization": f"Bearer {adminToken}","Content-Type": "application/json"
-d '{"model": "llama3.2","prompt": "Why is the sky blue?"}'

curl http://localhost:11434/api/chat/completions \
-H "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxOTBjYTQ1LTgxNzgtNGQ4NC1hYTAwLTNmYTQ4MWFiM2MwMiJ9.z2lI5wfu3uvuZ4ImS-QI3aEceiu1n-NhsIS2Yn-FfPE" \
-H "Content-Type": "application/json" \
-d '{ "model": "llama3.2:latest", "messages": [{"role":"test"}], "stream":false }'
