# YOLO Streamlit Document Analyzer

A Streamlit-based web application that uses **YOLO (Ultralytics)** to detect and analyze objects/regions in uploaded documents or images. The system supports image processing, object detection, and visualization of detected results in real time.

---

## 🚀 Features

- Upload images or documents (PDF/image support)
- Object detection using **YOLO (Ultralytics)**
- Visualization of bounding boxes on detected objects
- PDF-to-image conversion for document analysis
- Streamlit-based interactive UI
- Modular architecture (`app.py`, `detector.py`, `utils.py`)

---

## 🧠 Tech Stack

- Python 3.10+
- Streamlit
- Ultralytics YOLO
- OpenCV
- PyTorch
- pdf2image
- Pillow
- NumPy

---
## ⚙️ Installation

### 1. Clone the repository

git clone https://github.com/<your-username>/<repo-name>.git
cd YOLO
2. Create virtual environment
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Install system dependency (macOS only)
brew install poppler
▶️ Running the App
python -m streamlit run app.py

Then open:

http://localhost:8501
### Model Details

This project uses Ultralytics YOLO (You Only Look Once), a state-of-the-art real-time object detection model.

Framework: Ultralytics YOLOv8
Default model: yolov8n.pt (nano version, lightweight and fast)
Loaded using:
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
 