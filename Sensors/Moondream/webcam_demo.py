import sys
import os
import cv2
from PIL import Image

# Add the repo path to Python path
sys.path.append(os.path.abspath("moondream_repo"))

# Import from actual files
from moondream.torch.moondream import MoondreamModel
from moondream.torch.config import MoondreamConfig
import torch

config = MoondreamConfig()
# Make sure you're on the right device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Initialize the model (check if the model requires any config or tokenizer)
model = MoondreamModel(config=config).to(device)


# Capture image from webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot access webcam")

ret, frame = cap.read()
cap.release()

if not ret:
    raise RuntimeError("Failed to capture image")

img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

# Generate caption
print("Caption:", model.caption(img))
