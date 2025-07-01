import moondream as md
from PIL import Image

import time # Sleep interval

# TODO run on GPU

model = md.vl(model='./Sensors/Moondream/moondream05b.mf')
image = Image.open('./KB/ss.png')
encoded_image = model.encode_image(image)

while True:
    prompt = "What is the first two sentences in this image? If none, say 'No text'"
    response = model.query(encoded_image, prompt)
    print(response['answer'], flush=True)
    time.sleep(5)