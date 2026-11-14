from ultralytics import YOLO
from PIL import Image
import streamlit as st
import time

@st.cache_resource
def load_model():
    return YOLO("model/best.pt")

model = load_model()


def detect_regions(image):
    start_time = time.perf_counter()

    # Run the model on the image
    results = model.predict(source=image, verbose=False)

    # Get the first result (batch size 1)
    result = results[0]

    regions = []
    # result.boxes is a Boxes object containing detected boxes
    for box in result.boxes:

        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = box.conf[0].item()
        cls = int(box.cls[0].item())

        # Append detection tuple
        regions.append((x1, y1, x2, y2, conf, cls))
    
    elapsed = time.perf_counter() - start_time
    print(f"Total detection time: {elapsed:.3f} seconds")
    print(f"YOLO timing breakdown: {result.speed}")

    return regions