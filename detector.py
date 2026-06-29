from ultralytics import YOLO
from PIL import Image

model = YOLO("model/best.pt")  


def detect_regions(image):


    # Run the model on the image
    results = model(image)

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

    return regions