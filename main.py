# main.py
# Manages the sensors talking to the LLM via subprocesses

import sys
import time

import pexpect # Module which manages subprocess I/O

initDelay = 10 # Initial delay after starting LLM to wait for it to be ready for input
iterDelay = 5 # Increase delay for slower computers and/or to slow down iterations of prompting
startTime = time.time()

faceTrackerFile = open('faceTracker.txt', 'r+')
llmFile = open('llmFile.txt', 'r+')

faceTracker = pexpect.spawn('python -u ./Sensors/PythonFaceTracker/main.py', encoding='utf-8', logfile=faceTrackerFile)
llm = pexpect.spawn('ollama run llama3.2:1b', encoding='utf-8', logfile=sys.stdout) # Change logfile param to redirect outputs (e.g. to a file instead)

time.sleep(initDelay)
while faceTracker.status:
    # Get most recent output (TODO eventually change to seeking from end)
    faceTrackerFile.seek(0)
    out = faceTrackerFile.readlines()[-1]

    llm.sendline(out) # Write the facetracker output to the LLM's input
    llm.expect('>>>') # Stream the AI's output while awaiting the end of the response

faceTrackerFile.close() # Close files and terminate
llmFile.close()
faceTracker.terminate()
llm.terminate()