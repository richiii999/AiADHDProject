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
initDelay = 5 # Initial delay after starting LLM to wait for it to be ready for input
iterDelay = 5 # delay for each iteration of prompting

### SETUP: Must be done before running (on separate terminals / in background)
# ollama serve # Ollama automatically runs on Ubuntu, no need to serve
# DATA_DIR=./.open-webui uvx --python 3.11 open-webui@latest serve # Start open-webui server
# modprobe v4l2loopback video_nr=8,9 card_label="test1","test2" # Add video8/9 devices
    # v4l2-ctl --list-devices # Verify devices have appeared correctly
    # modprove -r v4l2loopback # Remove mod if it didnt work / want to change stuff

# The AI model itself is accessed via API

logFiles = [ # Log files, sensor output is periodically read from here and given to the AI
    open('./Logs/faceTracker.txt', 'r+'),
    open('./Logs/gazeTracker.txt', 'r+')
]


cmds = [ # Commands to run each sensor process
    'python ./Sensors/PythonFaceTracker/main.py', # Default: main.py, alt: OutputTest.py (for both)
    'python ./Sensors/PythonGazeTracker/example.py' # Default: example.py 
]

ffmpegLog = open('./Logs/ffmpegLog.txt', 'r+')
ffmpeg = subprocess.Popen('ffmpeg  -i /dev/video0 -f v4l2 -vcodec rawvideo -pix_fmt rgb24 /dev/video8 -f v4l2 -vcodec rawvideo -pix_fmt rgb24 /dev/video9 -loglevel quiet', shell=True)

time.sleep(2) # Couple sec buffer for ffmpeg to start streaming to video8/9 

# Sensor processes which record data to be passed to the AI
sensors = [subprocess.Popen(cmds[i], shell=True, stdout=logFiles[i]) for i in range(len(cmds))]

### RAG
KB = [ # Knowledge base, for RAG
    # './KB/TAD.pdf'
    './KB/OB_CH13.pptx'
    #'./KB/OB_CH14/pptx'
]

### Initialization of LLM 
# Set system prompt
# sysPrompt = ""
# with open("./LLM/initPrompt.txt", 'r') as f: 
#     for line in f.readlines(): sysPrompt += line.replace('\n',' ')

# with open("./LLM/create.txt") as f: pexpect.run(f.readline()) # Dumb way, but due to string formatting issues this is a workaround


# # Learning material upload & KB creation
# for path in KB:
#     file_ID = API.upload_file(path)['meta']['collection_name'][5:] # TODO ID is directly availible in another part of the dict without string slicing
#     API.add_file_to_knowledge(file_ID)

### Main loop
time.sleep(initDelay) # give servers & sensors time to start up
while True: # TODO how to close?
    sensorData = f"Time = {int(time.time() - startTime)} minutes, Aggregated Sensor data:\n"
    for f in logFiles: # Get most recent output per sensor 
        f.seek(0) # TODO eventually change to seeking from end of file instead of start
        sensorData += f.readlines()[-1]
    print(sensorData)

    # Prompt
    # response = API.chat_with_collection(sensorData,API.kb_id)
    # try: print(response['choices'][0]['message']['content']) # BUG: Need to manuallr refresh webui page, else 'model not found'
    # except: print(response)


    time.sleep(iterDelay)# Delay AFTER response (So you can actually read it)

for f in logFiles: f.close() # Close files and terminate procs
for s in sensors: s.terminate()
    