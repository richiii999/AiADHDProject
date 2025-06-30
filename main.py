# main.py
# Manages the sensors via subprocesses and prompts the LLM via the webui API

import sys
import subprocess # manages subprocess I/O (ollama / webui servers, sensors, and ffmpeg)
import time

import API # Contains API calls to webui

# TODO Knowledge file goes first, history file is added in endstudy func then removedm, then knowledge remioved knowledge is a verbose response based on summary

def EndStudySession(summaryPrompt, history_id): # Writes the response to summaryPrompt into the StudyHistory.txt file
    print('\nEnding study session...\n')
    with open('./KB/StudyHistory.txt', 'a') as f: f.write('\n' + API.chat_with_model(summaryPrompt)['choices'][0]['message']['content']) # Summary prompt and append result to the history file
    API.remove_file_from_knowledge(API.kb_id, history_id) # Delete the old file from the knowledge base
    # On next session, the new history is uploaded

def ReadFileAsLine(f) -> str: # Read a file as a str (multi-line)
    s = ''
    for line in f.readlines(): s += line.replace('\n',' ')
    return s

def AIScreenshot():
    subprocess.run(f'gnome-screenshot -w -f ./AiADHDProject/KB/img.png', shell=True) # Take a screenshot
    API.remove_file_from_knowledge() # remove old screenshot and replace the img.png


# Increase delay for slower computers. Eventually iterDelay is measured in minutes so it's okay
startTime = time.time()
initDelay = 5 # Initial delay after starting LLM to wait for it to be ready for input
iterDelay = 20 # delay for each iteration of prompting

### SETUP: Must be done before running (on separate terminals / in background)
# Get the shape_predictor... file from GDrive and put it in (mkdir) ./Sensors/PythonGazeTracker/gaze_tracking/trained_models/
# DATA_DIR=./.open-webui uvx --python 3.11 open-webui@latest serve # Start open-webui server
# DATA_DIR=./.open-webui open-webui@latest serve # Non-UV version of open-webui
# sudo modprobe v4l2loopback video_nr=8,9,10 # Add video8/9 devices
    # v4l2-ctl --list-devices # Verify devices have appeared correctly
    # sudo modprobe -r v4l2loopback # Remove mod if it didnt work / want to change stuff

# BUG: cv2.error: OpenCV(4.11.0) /io/opencv/modules/imgproc/src/bilateral_filter.dispatch.cpp:409: error: (-215:Assertion failed) !_src.empty() in function 'bilateralFilter'
# ^ Happens to GazeTracker when 2 people are on the screen at once I think, very strange

AI = True # Quickly change if AI / cams run rather than commenting out
CAM = True

HISTORY_ID = "" # Used to store the file id of the studyhistory.txt file on webui, so it can be updated without duplication later
SS_ID = "" # Stores the file_id of the screenshot

### Sensors & Subprocesses
logFiles = [ # Log files, sensor output is periodically read from here and given to the AI
    open('./Logs/faceTracker.txt', 'r+'),
    open('./Logs/gazeTracker.txt', 'r+'),
    open('./Logs/VLM.txt', 'r+')
]

for f in logFiles: 
    f.truncate(0) # Empty old logs
    f.write('\n') # Placeholder first log entry

cmds = [ # Commands to run each sensor process
    'python ./Sensors/PythonFaceTracker/main.py',
    'python ./Sensors/PythonGazeTracker/example.py'
    #'python ./Sensors/moondream/live_testcam.py'
]

if CAM: # Setup virtual cam devices and split original cam input to them
    ffmpeg = subprocess.Popen('ffmpeg  -i /dev/video0 \
    -f v4l2 -vcodec rawvideo -s 640x360 /dev/video8 \
    -f v4l2 -vcodec rawvideo -s 640x360 /dev/video9 \
    -f v4l2 -vcodec rawvideo -s 640x360 /dev/video10 \
    -loglevel quiet', shell=True)
    time.sleep(2) # Couple sec buffer for ffmpeg to start 

# Sensor processes which record data to be passed to the AI
sensors = [subprocess.Popen(cmds[i], shell=True, stdout=logFiles[i]) for i in range(len(cmds))] if CAM else [None]


KB = [ ### RAG Knowledge base
    './KB/StudyHistory.txt', # Summaries added by the AI after the end of study sessions. # MUST BE FIRST
    './KB/ADHD2.pdf', # ADHD Information 1, Some strats
    './KB/TeachingADHD.pdf', # ADHD Information 2, Good strats like quizzes and summaries
    './KB/OB_CH13.pptx' # Study Material 1
]

#IT's right here for creating the system prompt
if AI: ### Initialization of LLM 
    # Set system prompt from file # BUG: Need to manually refresh webui page when newly created, else 'model not found'
    with open("./LLM/SysPrompt.txt", 'r') as f: subprocess.run(f'curl http://localhost:11434/api/create -d \'{{ "model": "{API.model}", "from": "{API.base}", "system": "{ReadFileAsLine(f)}" }}\'', shell=True)

    # Learning material upload & KB creation
    for path in KB:
        file_ID = API.upload_file(path)['meta']['collection_name'][5:] # TODO ID is directly availible in another part of the dict without string slicing
        API.add_file_to_knowledge(file_ID) # BUG: If you get 'meta' key error here, reset API keys
        if HISTORY_ID == "": HISTORY_ID = file_ID # The first file uploaded is the study history file, which we dont want duplicates for

    time.sleep(initDelay) # give servers & sensors time to start up



# This below specifies the LOCATION of the screenshot and name of the file
# gnome-screenshot -w -f ./AiADHDProject/KB/img.png



while sensors[0].poll() == None: ### Main loop, ends when FaceTracker is stopped
    sensorData = f"Time = {int(time.time() - startTime)} minutes, Aggregated Sensor data:\n"
    for f in logFiles: # Get most recent output per sensor 
        f.seek(0)
        sensorData += f.readlines()[-1]
    print(sensorData)

    if AI:

        # Prompt
        response = API.chat_with_collection(sensorData, API.kb_id)
        try: print(response['choices'][0]['message']['content']) 
        except: print(response)

    time.sleep(iterDelay)

if AI: ### End of study: Summarize study session and append response to StudyHistory.txt
    with open('./LLM/SummaryPrompt.txt') as f: EndStudySession(ReadFileAsLine(f), HISTORY_ID)

for s in sensors[1:]: s.terminate()
for f in logFiles: f.close() 
ffmpeg.terminate()

print("\nExiting...\n")