# main.py
# Manages the sensors talking to the LLM via subprocesses

import sys
import time

import pexpect # Module which manages subprocess I/O

# Increase delay for slower computers. Eventually iterDelay is measured in minutes so it's okay
initDelay = 10 # Initial delay after starting LLM to wait for it to be ready for input
iterDelay = 5 # delay for each iteration of prompting
startTime = time.time()

# The AI model itself
llmFile = open('llmFile.txt', 'r+') # If needed, change logfile param to redirect outputs to this file instead
llm = pexpect.spawn('ollama run llama3.2', encoding='utf-8', logfile=sys.stdout)

logFiles = [ # Log files, sensor output is periodically read from here and given to the AI
    open('faceTracker.txt', 'r+')
    # Sensor 2 file ...
    # Sensor 3 file ...
]

sensors = [ # Sensors which record data to be passed to the AI
    pexpect.spawn('python -u ./Sensors/PythonFaceTracker/main.py', encoding='utf-8', logfile=logFiles[0])
    # Sensor 2 process ...
    # Sensor 3 process ...
]

time.sleep(initDelay) # Main loop
while sensors[0].status: # TODO how to close? For now just 'q' on FaceTracker to close everything
    sensorData = "Aggregated Sensor data (Each sensor on newline):"
    for f in logFiles: # Get most recent output per sensor 
        f.seek(0) # TODO eventually change to seeking from end of file instead of start
        sensorData += f.readlines()[-1]

    # TODO Multiline prompt has to start & end with triple quotes (""") I believe
    llm.sendline(sensorData) # Write the facetracker output to the LLM's input
    llm.expect('>>>') # Stream the AI's output while awaiting the end of the response

    time.sleep(iterDelay) # Delay AFTER response (So you can actually read it)

llmFile.close() # Close files and terminate
llm.terminate()
for f in logFiles: f.close() 
for s in sensors: s.terminate()
