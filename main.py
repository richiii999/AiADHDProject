# main.py
# Manages the sensors via subprocesses and prompts the LLM via the webui API

### SETUP: Must be done before running (on separate terminals / in background)
# reset packages / uv / venv:
    # delete all uv-related files and folders (.venv, uv.lock, pyproject.toml, .python-version)
    # deactivate, then uv-init, uv python pin 3.11.13, uv add -r requirements.txt
# Get the shape_predictor... file from GDrive and put it in (mkdir) ./Sensors/PythonGazeTracker/gaze_tracking/trained_models/
# DATA_DIR=./.open-webui uvx --python 3.11 open-webui@latest serve # Start open-webui server
# sudo modprobe v4l2loopback video_nr=8,9 # Add video8/9 devices
    # v4l2-ctl --list-devices # Verify devices have appeared correctly
    # sudo modprobe -r v4l2loopback # Remove mod if it didnt work / want to change stuff
# Connect Claude to openwebui: https://openwebui.com/f/justinrahb/anthropic
    # Download, then import from file on http://localhost:8080/admin/functions, 
    # remove the top / bottom html stuff. Also delete extra models if not needed
    # Once imported, click the gear 'valves' and insert the API key, turn it on

import sys
import subprocess # manages subprocess I/O (ollama / webui servers, sensors, and ffmpeg)
import time

import API # ./API.py: Contains API calls to webui

def PromptAI(prompt) -> str: # Prompt only, uses existing crontext
    global context
    context.append({"role":"user", "content":sanitize(prompt)})
    response = API.chat_with_collection(API.Models[modelNum], context, API.KBIDs[1])

    try: # try-except to print the error if it fails (usually 'model not found')
        response = response['choices'][0]['message']['content']
        if AUDIO: TTS(response)

        context.append({"role":"assistant", "content":sanitize(response)})
        return response
    except: print(response)

def EndStudySession(): # Writes the response to summaryPrompt into the StudyHistory.txt file
    print('\nEnding study session...\n')

    with open('./KB/StudyHistory.txt', 'a') as f1, open('./LLM/SummaryPrompt.txt', 'r') as p: 
        f1.write('\n' + PromptAI(ReadFileAsLine(p))) # Prompt Summary, append it to history file

    with open('./KB/StudyHistory.txt', 'r') as f1, open('./KB/Knowledge.txt', 'w') as f2, open('./LLM/KnowledgePrompt.txt', 'r') as p:
        global context
        context = [] # reset the context

        f2.truncate(0) # Replace old knowledge with new knowledge
        f2.write(PromptAI(ReadFileAsLine(p) + ReadFileAsLine(f1)))

    for i in API.KBIDs: API.delete_knowledge(i) # Delete knowledge bases
    subprocess.Popen("rm ./.open-webui/uploads/*", shell=True)
    subprocess.Popen("cd ./.open-webui/vector_db && rm -r `ls | grep -v 'chroma.sqlite3'`", shell=True)

def TTS(text): # Text to speech
    myobj = gTTS(text)
    myobj.save("response.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()

def ReadFileAsLine(f) -> str: # Read a file as a str (multi-line)
    s = ''
    for line in f.readlines(): s += sanitize(line).replace('\n',' ')
    return s

def sanitize(s) -> str: # Remove characters that cause issues from a str
    s = s.replace("\'", "")
    s = s.replace("\"", "")
    return s

def UserInput(inputPrompt, validinput=None) -> str: # User input verification. whenever 'q' by itself quits the main loop '' re-prompts, etc.
    i = input(inputPrompt)
    while i not in validinput:
        print("Invalid input, try again")
        time.sleep(1)
        i = input(inputPrompt)
    return i

startTime, initDelay, iterDelay = time.time(), 3, 5 # Timing delays
modelNum = int(UserInput("Please select a model # from the list:\n" + '\n'.join(['{}: {}'.format(i, val) for i, val in (enumerate(API.Models))]) + "\n>", [str(i) for i in range(len(API.Models))]))
userStudyTopic = input("What is your study topic? (Helps the AI use the provided files)\n>")

AUDIO = UserInput("Would you like Audio? (y/N)\n>", ['y','n',''])
if AUDIO == 'y':
    from gtts import gTTS
    import pygame

context = [] # The chat history for the AI, needs to be passed each time per chat

### Sensors & Subprocesses
print("Starting FFMPEG...") # Setup virtual cam devices and split original cam input to them
ffmpeg = subprocess.Popen('ffmpeg  -i /dev/video0 -f v4l2 -vcodec rawvideo -s 640x360 /dev/video8 -f v4l2 -vcodec rawvideo -s 640x360 /dev/video9 -loglevel quiet'.split(), stdin=subprocess.DEVNULL)
time.sleep(2) # Couple sec buffer for ffmpeg to start 

procs = { # {path : Log file}, sensor output is periodically read from here and given to the AI
    'python ./Sensors/PythonFaceTracker/main.py' : open('./Logs/faceTracker.txt', 'r+'),
    'python ./Sensors/PythonGazeTracker/example.py' : open('./Logs/gazeTracker.txt', 'r+')
    # 'python ./Sensors/Moondream/main.py' : open('./Logs/VLM.txt', 'r+')
}

for f in procs.values(): 
    f.truncate(0) # Empty old logs
    f.write('The user seems focused\n') # Placeholder first log entry

# Sensor processes which record data to be passed to the AI
print("Starting sensors...")
sensors = [subprocess.Popen(path.split(), stderr=subprocess.DEVNULL, stdout=log, stdin=subprocess.DEVNULL) for path,log in procs.items()]

KB = [ ### RAG 
    { # Expert knowledge the AI uses to make it's action space
        './KB/ADHD2.pdf':'', # ADHD Information 1, Some strats
        './KB/TeachingADHD.pdf':'' # ADHD Information 2, Good strats like quizzes and summaries
    },
    { # Users study material
        './KB/Knowledge.txt':'', # 'Knowledge' gained by AI after analyzing summaries. # MUST BE FIRST
        './KB/OB_CH13.pptx':'' # Study Material 1
    }
]

### Initialization of LLM 
print("Uploading files to knowledge base...")
for i in range(len(KB)): # wtf cant double iterate the list for some reason
    for file in KB[i].keys(): # NOTE: If you get 'meta' key error vv, reset API keys
        KB[i][file] = API.upload_file(file)['meta']['collection_name'][5:] # TODO ID is directly availible in another part of the dict without string slicing
        API.add_file_to_knowledge(KB[i][file], API.KBIDs[i])
        print(f'Uploaded file: {file} : {KB[i][file]} to knowledge base {API.KBIDs[i]}')

print("Getting action space via RAG...")
with open('./LLM/GenerateActions.txt', 'r') as f1, open("./LLM/SysPrompt.txt", 'r') as f2: # Set system prompt from file
    context.append({"role":"user", "content":ReadFileAsLine(f1)})
    listResponse = API.chat_with_collection(API.Models[modelNum],context, API.KBIDs[0])['choices'][0]['message']['content']

    sysprompt = ReadFileAsLine(f2)
    sysprompt += listResponse
    context = [{"role":"system", "content":sanitize(sysprompt)}] # The system prompt now contains the contents of sysprompt.txt appended with the list response

print("Starting Study Session...") ### Intro
time.sleep(initDelay) # give servers & sensors time to start up

# TODO: automatic prompt (vs timer prompt), have a bkg (no context) prompt, then only if 'yes' respond, do main prompt, else continue loop (20s between)
while sensors[0].poll() == None: ### Main loop, ends when FaceTracker is stopped
    sensorData = f"Time = {int(time.time() - startTime)} minutes, Aggregated Sensor data:\n"
    for f in procs.values(): # Get most recent output per sensor 
        f.seek(0)
        sensorData += f.readlines()[-1]
    print(sensorData)

    # subprocess.run(f'rm ./KB/ss.png; scrot -a 0,0,2560,1440 ./KB/ss.png', shell=True) # Take a ss for moondream

    # Prompt the AI WITHOUT CONTEXT and only sensors data for a 'yes' or 'no' response. Then only on 'yes' continue
    inp = "Based on the following sensor data, is the user in anyway not focused? 'yes' or 'no' only\n" + sensorData
    resp = API.chat_with_model(API.Models[modelNum], [{"role":"user", "content":sanitize(inp)}])['choices'][0]['message']['content'].lower()
    print("Distraction detection = " + resp)
    if resp == 'no': print("Not distracted, No action taken")
    else:
        print(PromptAI(sensorData)) # Send sensor data to get list of options
        print(PromptAI(input('\n>'))) # Have the user respond to the AI, picking a choice

    time.sleep(iterDelay)

EndStudySession() ### End of study: Summarize and append to StudyHistory.txt, then use that to create new knowledge

for s in sensors[1:]:
    ffmpeg.terminate() # ffmpeg sometimes doesnt terminate, so just spam it 
    s.terminate()
for f in procs.values(): f.close() 

print("\nExiting...\n")