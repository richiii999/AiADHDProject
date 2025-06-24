# main.py
# Manages the sensors via subprocesses and prompts the LLM via the webui API

import sys
import subprocess
import time

import cv2 # Camera
import pexpect # Module which manages subprocess I/O (ollama & webui servers)
import API # Contains API calls to webui

# Increase delay for slower computers. Eventually iterDelay is measured in minutes so it's okay
startTime = time.time()
initDelay = 10 # Initial delay after starting LLM to wait for it to be ready for input
iterDelay = 10 # delay for each iteration of prompting

### SETUP: Must be done before running (on separate terminals / in background)
# Get the shape_predictor... file from GDrive and put it in (mkdir) ./Sensors/PythonGazeTracker/gaze_tracking/trained_models/
# ollama serve # Ollama automatically runs on Ubuntu, no need to serve
# DATA_DIR=./.open-webui uvx --python 3.11 open-webui@latest serve # Start open-webui server
# DATA_DIR=./.open-webui open-webui@latest serve # Non-UV version of open-webui
# sudo modprobe v4l2loopback video_nr=8,9 card_label="test1","test2" # Add video8/9 devices
    # v4l2-ctl --list-devices # Verify devices have appeared correctly
    # sudo modprobe -r v4l2loopback # Remove mod if it didnt work / want to change stuff
# install ffmpeg if you dont already have it

# The AI model itself is accessed via API
try: # Very dumb way of doing it, there has to be a better way to handle CTRL-C / crashes
    ### Sensors & Subprocesses
    logFiles = [ # Log files, sensor output is periodically read from here and given to the AI
        open('./Logs/faceTracker.txt', 'r+'),
        open('./Logs/gazeTracker.txt', 'r+')
    ]

    for f in logFiles: 
        f.truncate(0) # Empty old logs
        f.write('The User seems focused.\n')

    cmds = [ # Commands to run each sensor process
        'python ./Sensors/PythonFaceTracker/main.py', # Default: main.py, alt: OutputTest.py (for both)
        'python ./Sensors/PythonGazeTracker/example.py' # Default: example.py 
    ]

    ffmpeg = subprocess.Popen('ffmpeg  -i /dev/video0 -f v4l2 -vcodec rawvideo -s 640x360 /dev/video8 -f v4l2 -vcodec rawvideo -s 640x360 /dev/video9 -loglevel quiet', shell=True)
    time.sleep(2) # Couple sec buffer for ffmpeg to start streaming to video8/9 

    # Sensor processes which record data to be passed to the AI
    sensors = [subprocess.Popen(cmds[i], shell=True, stdout=logFiles[i]) for i in range(len(cmds))]

    ### RAG
    KB = [ # Knowledge base, for RAG
        './KB/ADHD2.pdf', # ADHD Information 1, Some strats
        './KB/TeachingADHD.pdf', # ADHD Information 2, Good strats like quizzes and summaries
        './KB/OB_CH13.pptx' # Study Material 1
    ]

    ### Initialization of LLM 
    # TODO Reading system prompt from a file with newlines would be better than having to manually remove it and put it in the curl command
    # sysPrompt = "" # Set system prompt
    # with open("./LLM/initPrompt.txt", 'r') as f: 
    #     for line in f.readlines(): sysPrompt += line.replace('\n',' ')

    with open("./LLM/create_ADHD.txt") as f: pexpect.run(f.readline()) # Dumb way, but due to string formatting issues this is a workaround

    # Learning material upload & KB creation
    for path in KB:
        file_ID = API.upload_file(path)['meta']['collection_name'][5:] # TODO ID is directly availible in another part of the dict without string slicing
        API.add_file_to_knowledge(file_ID)

    ### Main loop
    time.sleep(initDelay) # give servers & sensors time to start up
    while True:
        sensorData = f"Time = {int(time.time() - startTime)} minutes, Aggregated Sensor data:\n"
        for f in logFiles: # Get most recent output per sensor 
            f.seek(0) # TODO eventually change to seeking from end of file instead of start
            sensorData += f.readlines()[-1]
        print(sensorData)

        # Prompt
        response = API.chat_with_collection(sensorData,API.kb_id)
        try: print(response['choices'][0]['message']['content']) # BUG: Need to manuallr refresh webui page when created, else 'model not found'
        except: print(response)

        print('delayStart')
        time.sleep(iterDelay) # Delay AFTER response (So you can actually read it)
        print('delayEnd')

except Exception as e: # Gracefully close subprocesses on close / crash
    print(e)
    for s in sensors: s.terminate()
    for f in logFiles: f.close() # Close files and terminate procs
    ffmpeg.terminate()
    print("\nExiting...\n")