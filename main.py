# main.py
# Manages the sensors via subprocesses and prompts the LLM via the webui API

### SETUP: Must be done before running (on separate terminals / in background)
# Get the shape_predictor... file from GDrive and put it in (mkdir) ./Sensors/PythonGazeTracker/gaze_tracking/trained_models/
# DATA_DIR=./.open-webui uvx --python 3.11 open-webui@latest serve # Start open-webui server
# DATA_DIR=./.open-webui open-webui@latest serve # Non-UV version of open-webui
# sudo modprobe v4l2loopback video_nr=8,9,10 # Add video8/9 devices
    # v4l2-ctl --list-devices # Verify devices have appeared correctly
    # sudo modprobe -r v4l2loopback # Remove mod if it didnt work / want to change stuff
# reset packages / uv / venv:
    # delete all uv-related files and folders (.venv, uv.lock, pyproject.toml, .python-version)
    # deactivate, then uv-init, uv python pin 3.11.13, uv add -r requirements.txt

import sys
import subprocess # manages subprocess I/O (ollama / webui servers, sensors, and ffmpeg)
import time

import API # ./API.py: Contains API calls to webui

AI, CAM = True, True # Quickly change if AI / cams run rather than commenting out
startTime, initDelay, iterDelay = time.time(), 5, 4 # Timing delays

def PromptAI(prompt):
    response = API.chat_with_collection(prompt)
    try: print(response['choices'][0]['message']['content']) 
    except: print(response) # try-except to print the error if it fails (usually 'model not found')

def EndStudySession(knowledgeFileID): # Writes the response to summaryPrompt into the StudyHistory.txt file
    print('\nEnding study session...\n')

    with open('./KB/StudyHistory.txt', 'a') as f1: 
        with open('./LLM/SummaryPrompt.txt', 'r') as p1: f1.write('\n' + API.chat_with_model(ReadFileAsLine(p1))['choices'][0]['message']['content']) # Summary append to history file
        historyID = API.upload_file('./KB/StudyHistory.txt') # Upload history
        
        with open('./KB/Knowledge.txt', 'r+') as f2: # Update the knowledge based on history + current session
            f2.truncate(0)
            with open('./LLM/KnowledgePrompt.txt', 'r') as p2: f2.write(API.chat_with_file(ReadFileAsLine(p2), historyID)['choices'][0]['message']['content'])

    # TODO Delete history and knowledge file # There doesnt seem to be an API to delete files, so the .open-webui/uploads folder will keep growing 
    API.remove_file_from_knowledge(knowledgeFileID) # Remove current Knowledge from KB (new one is uploaded on next start)

def ReadFileAsLine(f) -> str: # Read a file as a str (multi-line)
    s = ''
    for line in f.readlines(): s += line.replace('\n',' ')
    return s

### Sensors & Subprocesses
knowledgeFileID = "" # Used to store the file id of the studyhistory.txt file on webui, so it can be updated without duplication later
logFiles = [ # Log files, sensor output is periodically read from here and given to the AI
    open('./Logs/faceTracker.txt', 'r+'),
    open('./Logs/gazeTracker.txt', 'r+'),
    open('./Logs/VLM.txt', 'r+')
]

for f in logFiles: 
    f.truncate(0) # Empty old logs
    f.write('The user seems focused\n') # Placeholder first log entry

cmds = [ # Commands to run each sensor process
    'python ./Sensors/PythonFaceTracker/main.py',
    'python ./Sensors/PythonGazeTracker/example.py', 
    'python ./Sensors/Moondream/main.py'
]

if CAM: # Setup virtual cam devices and split original cam input to them
    ffmpeg = subprocess.Popen('ffmpeg  -i /dev/video0 -f v4l2 -vcodec rawvideo -s 640x360 /dev/video8 -f v4l2 -vcodec rawvideo -s 640x360 /dev/video9 -loglevel quiet', shell=True)
    time.sleep(2) # Couple sec buffer for ffmpeg to start 

# Sensor processes which record data to be passed to the AI
sensors = [subprocess.Popen(cmds[i], shell=True, stdout=logFiles[i]) for i in range(len(cmds))] if CAM else [None]

# TODO maybe swtich KB to a dict and have fileIDs as keys so can just loop over it and remove all fileids from the kb at end, also fixes duplicate warnings
KB = [ ### RAG Knowledge base
    './KB/Knowledge.txt', # 'Knowledge' gained by AI after analyzing summaries. # MUST BE FIRST
    './KB/ADHD2.pdf', # ADHD Information 1, Some strats
    './KB/TeachingADHD.pdf', # ADHD Information 2, Good strats like quizzes and summaries
    './KB/OB_CH13.pptx' # Study Material 1
]

if AI: ### Initialization of LLM 
    # Set system prompt from file # BUG: Need to manually refresh webui page when newly created, else 'model not found'
    with open("./LLM/SysPrompt.txt", 'r') as f: subprocess.run(f'curl http://localhost:11434/api/create -d \'{{ "model": "{API.model}", "from": "{API.base}", "system": "{ReadFileAsLine(f)}" }}\'', shell=True)

    # Learning material upload & KB creation
    for path in KB:
        file_ID = API.upload_file(path) 
        # print(file_ID)
        file_ID = file_ID['meta']['collection_name'][5:] # TODO ID is directly availible in another part of the dict without string slicing
        
        API.add_file_to_knowledge(file_ID) # NOTE: If you get 'meta' key error ^^, reset API keys
        if knowledgeFileID == "": knowledgeFileID = file_ID # The first file uploaded is the study history file, which we dont want duplicates for


time.sleep(initDelay) # give servers & sensors time to start up
while sensors[0].poll() == None: ### Main loop, ends when FaceTracker is stopped
    sensorData = f"Time = {int(time.time() - startTime)} minutes, Aggregated Sensor data:\n"
    for f in logFiles: # Get most recent output per sensor 
        f.seek(0)
        sensorData += f.readlines()[-1]
    print(sensorData)

    subprocess.run(f'rm ./KB/ss.png; scrot ./KB/ss.png', shell=True) # Take a ss for moondream

    if AI: PromptAI(sensorData)

    time.sleep(iterDelay)

if AI: EndStudySession(knowledgeFileID) ### End of study: Summarize and append to StudyHistory.txt, then use that to create new knowledge

for s in sensors[1:]: s.terminate()
for f in logFiles: f.close() 
ffmpeg.terminate()
print("\nExiting...\n")