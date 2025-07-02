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

# Capture a frame from webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot access webcam")
ret, frame = cap.read()
cap.release()
if not ret:
    raise RuntimeError("Failed to capture image")

# Convert BGR to RGB for PIL
img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

# Generate caption and answer a question
caption = model.caption(img, length="short")["caption"]
print("Caption:", caption)

long_caption = model.caption(img, length="normal")["caption"]
print("Detailed Caption:", long_caption)

answer = model.query(img, "How many people are in this image?")["answer"]
print("Answer:", answer)


short_caption = model.answer_question(img, "Give a short caption of this image.")
long_caption2 = model.answer_question(img, "Describe the image in detail, including people, background, and actions.")


print("Short caption:", short_caption)
print("Long caption:", long_caption)
