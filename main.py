# main.py
# Manages the sensors talking to the LLM via subprocesses

import sys
import time

import pexpect # Module which manages subprocess I/O

def multiLinePrompt(s): return '"""\n' + s + '"""\n'

# Increase delay for slower computers. Eventually iterDelay is measured in minutes so it's okay
initDelay = 15 # Initial delay after starting LLM to wait for it to be ready for input
iterDelay = 10 # delay for each iteration of prompting
startTime = time.time()

# The AI model itself
llmFile = open('llmFile.txt', 'r+') # If needed, change logfile param to redirect outputs to this file instead
llm = pexpect.spawn('ollama run llama3.2', encoding='utf-8')
llm.logfile_read=sys.stdout

# PROMPTING
# API prompt format, can do pexpect.run(f"vvv{prompt}")
    # curl http://localhost:11434/api/generate -d '{
    # "model": "llama3.2:3b-instruct-fp16",
    # "prompt": "Why is the sky blue?", 
    # "stream": false
    # }'
# No response back, it stays on the webui

logFiles = [ # Log files, sensor output is periodically read from here and given to the AI
    open('faceTracker.txt', 'r+'),
    open('gazeTracker.txt', 'r+'),
    open('llavaOutput.txt', 'r+') # TODO does llava output go over multiple newlines? How to separate
]

sensors = [ # Sensor processes which record data to be passed to the AI
    # pexpect.spawn('python -u ./Sensors/PythonFaceTracker/main.py', encoding='utf-8', logfile=logFiles[0])
    # pexpect.spawn('python -u ./Sensors/PythonGazeTracker/main.py', encoding='utf-8', logfile=logFiles[1])
    # pexpect.spawn('ollama run llava', encoding='utf-8', logfile=logFiles[2])
]

# Initialization of LLM (sensors also starting up during this time)
time.sleep(initDelay) 
#with open('initPrompt.txt', 'r') as initPrompt:
 #   temp = llm.logfile
 #   llm.logfile = llmFile # Discard initial response

#    prompt = ''
#    for line in initPrompt.readlines(): prompt += line
#    llm.send(multiLinePrompt(prompt))

#    llm.expect('>>>')
#    llm.logfile = temp

# Main loop
while True: # TODO how to close? For now just 'q' on FaceTracker to close everything
    sensorData = f"Time = {time.time() - startTime} minutes, Aggregated Sensor data (Each sensor on newline):\n" # TODO remove time from facetracker
    for f in logFiles: # Get most recent output per sensor 
        f.seek(0) # TODO eventually change to seeking from end of file instead of start
        sensorData += f.readlines()[-1]

    llm.send(multiLinePrompt(sensorData))
    llm.expect('>>>')
    time.sleep(iterDelay) # Delay AFTER response (So you can actually read it)

llmFile.close() # Close files and terminate procs
llm.terminate()
for f in logFiles: f.close() 
for s in sensors: s.terminate()
