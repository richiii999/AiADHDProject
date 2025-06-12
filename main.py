# main.py
# Manages the sensors talking to the LLM via subprocesses

import sys
import time
import subprocess

import pexpect

sleepytime = 2
startTime = time.time()

faceTrackerFile = open('faceTracker.txt', 'r+')
llmFile = open('llmFile.txt', 'w')

llm = pexpect.spawn('ollama run llama3.2:1b', encoding='utf-8')
llm.logfile_send = sys.stdout # redirect all llm output to stdout

time.sleep(sleepytime)
while True:
    faceTrackerFile.seek(0)
    out = faceTrackerFile.readlines()[-1] # Get most recent output (TODO eventually change to seeking from end)

    llm.sendline(out) # Write the facetracker output to the LLM's input
    llm.expect('>>>')

faceTrackerFile.close()
llmFile.close()

llm.terminate()