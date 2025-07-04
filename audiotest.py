from gtts import gTTS
import pygame

import API

AUDIO = True

def PromptAI(prompt):
    response = API.chat_with_model(prompt)

    try: # try-except to print the error if it fails (usually 'model not found')
        response = response['choices'][0]['message']['content']
        print(response)
        if AUDIO: TTS(response)
    except: print(response)

def TTS(text):
    myobj = gTTS(text)
    myobj.save("response.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy(): pygame.time.Clock().tick(10) # Wait for response to finish before continuing

while True: PromptAI("test")

