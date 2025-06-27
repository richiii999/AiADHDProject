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

while True:
    cap = cv2.VideoCapture(10) # Capture a frame from webcam
    if not cap.isOpened(): raise RuntimeError("Cannot access webcam")
    ret, frame = cap.read()
    cap.release()
    if not ret: raise RuntimeError("Failed to capture image")

    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) # Convert BGR to RGB for PIL

    short_caption = model.answer_question(img, "Give a short caption of the individual in the image. Do they seem focused or not? Do not comment about the environment")
    print("Short caption:", short_caption)
