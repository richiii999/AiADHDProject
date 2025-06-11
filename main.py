# main.py
# Manages the sensors talking to the LLM via subprocesses

# import os
import subprocess
import time

# pexpect # Used to manage subprocesses so we can write multiple times to the

startTime = time.time()

faceTrackerFile = open('faceTracker.txt', 'r+')
# faceTrackerFile.write("test\ntest")
llmFile = open('llmFile.txt', 'r+')

faceTracker = subprocess.Popen(['python','-u', './Sensors/PythonFaceTracker/main.py'], stdin=subprocess.PIPE, stdout=faceTrackerFile)
llm = subprocess.Popen('ollama run llama3.2', stdin=subprocess.PIPE, shell=True, text=True)

time.sleep(8) # Wait for facetracker to fully start
for i in range(2):
    time.sleep(3)
    print(f"Time={int(time.time()-startTime)}")
    
    faceTrackerFile.seek(0)
    out = faceTrackerFile.readlines()[-1] # Get most recent output (TODO eventually change to seeking)
    print(str(out)) 

    llm.stdin.write(out + '\n') # Write the facetracker output to the LLM's input
    llm.stdin.flush()

llm.stdin.write("print all previous input, but start each new line with '--'\n Do not make a script or command, just print the input")

faceTrackerFile.close()
llmFile.close()

# TODO turn off subprocess from this file