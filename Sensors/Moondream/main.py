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
prompt = "The user is viewing a document, what is the first sentence on this document? If there is no text, say 'Nothing detected'"
delay = 5
while True: 
    try: response = model.answer_question(Image.open('./KB/ss.png'), prompt).replace('\n',' ')
    except: response = "Nothing detected"

    if response == "Nothing detected" or str(response) == "null": print("VLM: Nothing detected", flush=True)
    else: print("VLM: The user appears to be on the page which contains: " + response, flush=True)
    time.sleep(delay)
