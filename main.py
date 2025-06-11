# main.py
# Manages the sensors talking to the LLM via subprocesses

# import os
import subprocess
import time

startTime = time.time()

faceTrackerFile = open('faceTracker.txt', 'r+')
# faceTrackerFile.write("test\ntest")
llmFile = open('llmFile.txt', 'r+')

faceTracker = subprocess.Popen(['python','-u', './Sensors/PythonFaceTracker/main.py'], stdin=subprocess.PIPE, stdout=faceTrackerFile, universal_newlines=True)
llm = subprocess.Popen('ollama run llama3.2', stdin=subprocess.PIPE, shell=True, text=True, universal_newlines=True)

time.sleep(8) # Wait for facetracker to fully start
while faceTracker.poll() == None:
    time.sleep(3)
    print(f"Time={int(time.time()-startTime)}")
    
    faceTrackerFile.seek(0)
    out = faceTrackerFile.readlines()[-1] # Get most recent output (TODO eventually change to seeking)
    print(str(out)) 

    llm.stdin.write(out + '\r\n') # Write the facetracker output to the LLM's input
    llm.stdin.flush()

llm.stdin.write("print all previous input\nDo not make a script or command, just print the input and nothing else.")

faceTrackerFile.close()
llmFile.close()

faceTracker.kill()

time.sleep(10)
llm.kill()