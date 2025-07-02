import cv2
from PIL import Image
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "vikhyatk/moondream2"
revision = "2025-04-14"  # Or the latest available version

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    revision=revision,
    trust_remote_code=True,
    device_map={"": device}
)

tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)


### AI ADHD stuff
import time 
prompt = "The user is viewing a document, what are the first two sentences on this document? If there is no text, say 'No text availible'" # If there does not appear to be a slide in the image then say 'The user seems distracted.'"
delay = 5
while True: 
    print(("VLM: The user appears to be on the page which contains: " + model.answer_question(Image.open('./KB/ss.png'), prompt)).replace('\n',' '), flush=True)
    time.sleep(5)
