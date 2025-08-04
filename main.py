# main.py

import sys
import time
import subprocess # manages subprocess I/O (ollama / webui servers, sensors, and ffmpeg)

import API # ./API.py: Contains API calls to webui

def PromptAI(prompt) -> str:
    global context
    context.append({"role":"user", "content":sanitize(prompt)})
    response = API.chat_with_collection(API.Models[modelNum], context, API.KBIDs[1])

    response = response['choices'][0]['message']['content']
    context.append({"role":"assistant", "content":sanitize(response)})

    if AUDIO: TTS(response)
    return response

def EndStudySession(): # Writes the response to summaryPrompt into the StudyHistory.txt file
    print('\nEnding study session...\n')

    with open('./KB/StudyHistory.txt', 'a') as f1, open('./LLM/SummaryPrompt.txt', 'r') as p: f1.write('\n' + PromptAI(ReadFileAsLine(p))) # Prompt Summary, append it to history file
    with open('./KB/StudyHistory.txt', 'r') as f1, open('./KB/Knowledge.txt', 'w') as f2, open('./LLM/KnowledgePrompt.txt', 'r') as p:
        global context
        context = [] # reset the context

        f2.truncate(0) # Replace old knowledge with new knowledge
        f2.write(PromptAI(ReadFileAsLine(p) + ReadFileAsLine(f1)))

    for i in API.KBIDs: API.delete_knowledge(i) # Delete knowledge bases
    subprocess.run("rm ./.open-webui/uploads/*", shell=True)
    subprocess.run("cd ./.open-webui/vector_db && rm -r `ls | grep -v 'chroma.sqlite3'`", shell=True)

def TTS(text):
    myobj = gTTS(text)
    myobj.save("response.mp3")
    mixer.init()
    mixer.music.load("response.mp3")
    mixer.music.play()

def ReadFileAsLine(f) -> str:
    s = ''
    for line in f.readlines(): s += sanitize(line).replace('\n',' ')
    return s

def sanitize(s) -> str: # Remove characters that cause issues from a str
    s = s.replace("\'", "")
    s = s.replace("\"", "")
    return s

def UserInput(inputPrompt, validinput=None) -> str: # User input verification
    i = input(inputPrompt)
    while i not in validinput:
        print("Invalid input, try again")
        i = input(inputPrompt)
    return i

def Sense() -> str: # Gather output from the sensors
    sensorData = f"Time = {int(time.time() - startTime)} minutes, Aggregated Sensor data:\n"
    for f in procs.values(): # Get most recent output per sensor 
        f.seek(0)
        sensorData += f.readlines()[-1]
    return sensorData

def DistractionDetection(sensorData) -> str: # Prompt the AI WITHOUT CONTEXT for a 'yes' or 'no' response
    inp = "Based on the following sensor data, is the user in anyway not focused? 'yes' or 'no' only\n" + sensorData
    resp = API.chat_with_model(API.Models[modelNum], [{"role":"user", "content":sanitize(inp)}])['choices'][0]['message']['content'].lower().replace('.','')
    return resp

### Initialization
print("Welcome to...") # Title screen
time.sleep(1)
print("       ___           ___           ___           ___           ___                   ")
print("      /\\__\\         /\\  \\         /\\__\\         /\\  \\         /\\__\\        ")
print("     /:/ _/_       /::\\  \\       /:/  /         \\:\\  \\       /:/ _/_            ")
print("    /:/ /\\__\\     /:/\\:\\  \\     /:/  /           \\:\\  \\     /:/ /\\  \\      ")
print("   /:/ /:/  /    /:/  \\:\\  \\   /:/  /  ___   ___  \\:\\  \\   /:/ /::\\  \\       ")
print("  /:/_/:/  /    /:/__/ \\:\\__\\ /:/__/  /\\__\\ /\\  \\  \\:\\__\\ /:/_/:/\\:\\__\\ ")
print("  \\:\\/:/  /     \\:\\  \\ /:/  / \\:\\  \\ /:/  / \\:\\  \\ /:/  / \\:\\/:/ /:/  / ")
print("   \\::/__/       \\:\\  /:/  /   \\:\\  /:/  /   \\:\\  /:/  /   \\::/ /:/  /       ")
print("    \\:\\  \\        \\:\\/:/  /     \\:\\/:/  /     \\:\\/:/  /     \\/_/:/  /      ")
print("     \\:\\__\\        \\::/  /       \\::/  /       \\::/  /        /:/  /           ")
print("      \\/__/         \\/__/         \\/__/         \\/__/         \\/__/         \n\n")
time.sleep(1)

startTime, initDelay, iterDelay = time.time(), 3, 5 # Timing delays

API.Models += subprocess.check_output("ollama list | grep -v NAME | awk '{print $1}'", shell=True).decode('utf-8').split('\n')[:-1] # Get the list of models from ollama (formatting to remove the col names)
modelNum = int(UserInput("Please select a model # from the list:\n" + '\n'.join(['{}: {}'.format(i, val) for i, val in (enumerate(API.Models))]) + "\n>", [str(i) for i in range(len(API.Models))]))

userStudyTopic = input("What is your study topic? (Helps the AI use the provided files)\n>")

AUDIO = UserInput("Would you like Audio? (y/N)\n>", ['y','n',''])
if AUDIO == 'y':
    from gtts import gTTS # TTS
    from pygame import mixer # Audio

context = [] # The chat history for the AI, needs to be passed each time per chat

### Sensors & Subprocesses
print("Starting FFMPEG...") # Setup virtual cam devices and split original cam input to them
ffmpeg = subprocess.Popen('ffmpeg  -i /dev/video0 -f v4l2 -vcodec rawvideo -s 640x360 /dev/video8 -f v4l2 -vcodec rawvideo -s 640x360 /dev/video9 -loglevel quiet'.split(), stdin=subprocess.DEVNULL)
time.sleep(2) # Couple sec buffer for ffmpeg to start 

procs = { # {path : Log file}, sensor output is periodically read from here and given to the AI
    'python ./Sensors/PythonFaceTracker/main.py'    : open('./Logs/faceTracker.txt', 'r+'),
    'python ./Sensors/PythonGazeTracker/example.py' : open('./Logs/gazeTracker.txt', 'r+')
}

for f in procs.values(): 
    f.truncate(0) # Empty old logs
    f.write('The user seems focused\n') # Placeholder first log entry

print("Starting sensors...") # Sensor processes which record data to be passed to the AI
sensors = [subprocess.Popen(path.split(), stderr=subprocess.DEVNULL, stdout=log, stdin=subprocess.DEVNULL) for path,log in procs.items()]
KB = [ ### RAG 
    { # Expert knowledge the AI uses to make it's action space
        './KB/ADHD2.pdf'       :'', # ADHD Information 1, Some strats
        './KB/TeachingADHD.pdf':''  # ADHD Information 2, Good strats like quizzes and summaries
    },
    { # Users study material
        './KB/Knowledge.txt':'', # 'Knowledge' gained by AI after analyzing summaries. # MUST BE FIRST
        './KB/OB_CH13.pptx' :''  # Study Material 1
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

while sensors[0].poll() == None: ### Main loop, ends when FaceTracker is stopped
    sensorData = Sense()
    print(sensorData)

    if DistractionDetection(sensorData) == 'no': print("Not distracted, No action taken")
    else:
        print(PromptAI(sensorData)) # Send sensor data to get list of options
        print(PromptAI(input('\n>'))) # Have the user respond to the AI, picking a choice
        
    time.sleep(iterDelay)
EndStudySession() ### End of study: Summarize and append to StudyHistory.txt, then use that to create new knowledge

ffmpeg.terminate() # ffmpeg sometimes doesnt terminate, so just spam it 
for s in sensors[1:]: s.terminate()
for f in procs.values(): f.close() 

print("\nExiting...\n")

# todo 'q' to quit