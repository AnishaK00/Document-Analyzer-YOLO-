# Document Analyzer using YOLO

A deep learning-based document analysis system that detects and classifies structural elements such as text blocks, tables, and figures using a custom-trained YOLO object detection model.

**[Try the Live Demo](https://yolo-document-analyzer.streamlit.app/)**

## Features

- Detects text regions, tables, and figures.
- Supports image and PDF uploads.
- Visualizes detected regions with bounding boxes and confidence scores.
- Interactive web interface built with Streamlit.
- Modular detection and image-processing pipeline.

## Tech Stack

- **Language:** Python
- **Model:** YOLO (Ultralytics)
- **Deep Learning:** PyTorch
- **Image Processing:** OpenCV, Pillow, NumPy
- **Frontend:** Streamlit

## Model Details

- **Architecture:** YOLO Object Detection
- **Classes:** Text, Table, Figure
- **Input Resolution:** 640 × 640
- **Output:** Bounding boxes, class labels, and confidence scores.

The model was trained on a custom dataset of annotated document pages.

## Project Structure

```text
Document-Analyzer-YOLO-/
├── app.py
├── detector.py
├── utils.py
├── models/
│   └── best.pt
├── uploads/
├── outputs/
└── requirements.txt
```

## Installation & Usage

**1. Clone the repository**

```bash
git clone https://github.com/AnishaK00/Document-Analyzer-YOLO-.git
cd Document-Analyzer-YOLO-
```

**2. Create a virtual environment and install dependencies**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Run the application**

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.


