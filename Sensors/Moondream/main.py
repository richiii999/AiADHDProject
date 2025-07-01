import moondream as md
from PIL import Image

import time # Sleep interval

model = md.vl(model='./Sensors/Moondream/moondream05b.mf')
image = Image.open('./KB/ss.png')
encoded_image = model.encode_image(image)

while True:
    prompt = "What is the uppermost sentence in this image? If none, say 'No text detected'"
    response = model.query(encoded_image, prompt)
    print("VLM: The user is near the following text:" + response['answer'].replace('\n',' '), flush=True)
    time.sleep(5)