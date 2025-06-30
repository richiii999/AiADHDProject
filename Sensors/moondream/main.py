import cv2
from PIL import Image
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import time 

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

delay = 5
prompt = "The user should be viewing a document, what page or slide are they on? \
Respond as 'The user seems to be on page X.' where X is the page or slide number. \
If there does not appear to be a document in the image, respond as 'The user seems distracted.'"

while True: 
    print("VLM:", model.answer_question(Image.open('./KB/ss.png'), prompt))
    time.sleep(5) # Delay before next prompt
