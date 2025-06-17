# main.py
# Manages the sensors via subprocesses and prompts the LLM via the webui API

import sys
import time

import pexpect # Module which manages subprocess I/O (ollama & webui servers)
import API # Contains API calls to webui. The AI model itself is accessed via API

### Servers must be started manually in their own terminals
# DATA_DIR=./.open-webui uvx --python 3.11 open-webui@latest serve
# ollama serve

def GetSensorData() -> str:
    sensorData = f"Time = {int(time.time() - startTime)} minutes, Aggregated Sensor data:\n"
    for f in logFiles: # Get most recent output per sensor 
        f.seek(0) # TODO eventually change to seeking from end of file instead of start
        sensorData += f.readlines()[-1] + '\n'
    return sensorData

# TODO, sensors should automitcally trigger a prompt, rather than just a timer.
# perhaps some combination of timer / trigger? Like when a major distraction is detected it sets timer to 0

# Increase delay for slower computers. Eventually iterDelay is measured in minutes so it's okay
initDelay = 5 # Initial delay after starting LLM to wait for it to be ready for input
iterDelay = 5 # delay for each iteration of prompting
startTime = time.time()

logFiles = [ # Log files, sensor output is periodically read from here and given to the AI
    open('./Logs/faceTracker.txt', 'r+'),
    open('./Logs/gazeTracker.txt', 'r+'),
]

sensors = [ # Sensor processes which record data to be passed to the AI
    # pexpect.spawn('python -u ./Sensors/PythonFaceTracker/main.py', encoding='utf-8', logfile=logFiles[0])
    # pexpect.spawn('python -u ./Sensors/PythonGazeTracker/main.py', encoding='utf-8', logfile=logFiles[1])
]

KB_ID = API.kb_id # Used to refer to the KB in prompts, updated when KB files are uploaded
KB = [ # Knowledge base, for RAG
    #'./KB/TAD.pdf'
    #'./KB/OB_CH13.pptx'
    #'./KB/OB_CH14.pptx'
]

### Initialization of LLM 
sysPrompt = ""
with open("./Logs/initPrompt2.txt", 'r') as f: 
    for line in f.readlines(): sysPrompt += line.replace('\n',' ')

with open("./create.txt") as f: pexpect.run(f.readline()) # Dumb way of doing it, but due to string formatting issues this is a workaround

time.sleep(initDelay) # give servers & sensors time to start up
### Learning material upload & KB creation
for path in KB: # TODO, duplicate file uploads mess this up. have to manually remove from webui each time
    file_ID = API.upload_file(path)['meta']['collection_name'][5:] # TODO ID is directly availible in another part of the dict without string slicing
    API.add_file_to_knowledge(file_ID)

### Main loop
while True: # TODO how to close? For now just 'q' on FaceTracker to close everything
    sensorData = GetSensorData()
    print(sensorData)

    ### Chat with model
    #print(API.chat_with_model("who are you")['choices'][0]['message']['content'])
    
    ### Chat with collection
    print(API.chat_with_collection(sensorData,KB_ID)['choices'][0]['message']['content'])

    time.sleep(iterDelay) # Delay AFTER response (So you can actually read it)

for f in logFiles: f.close() # Close files and terminate procs
for s in sensors: s.terminate()
    