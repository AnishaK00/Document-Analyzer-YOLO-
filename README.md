Overview

This project is a deep learning-based document analysis system that detects and classifies structural components in documents such as text blocks, tables, and figures using a custom-trained YOLO (You Only Look Once) object detection model.

It provides a simple web interface built with Streamlit, allowing users to upload images or PDFs and visualize detected regions.

Features
Detects document elements:
Text regions
Tables
Figures/images
YOLO-based real-time object detection
Supports image and PDF inputs
Visualizes bounding boxes on detected elements
Streamlit-based interactive UI
Modular backend (separated detection and utility logic)
Tech Stack
Python 3.10+
YOLO (Ultralytics / custom-trained model)
OpenCV
PyTorch
Streamlit
Pillow (PIL)
NumPy
Project Structure
project/
│── app.py                  # Streamlit UI entry point
│── detector.py            # YOLO inference logic
│── utils.py               # Helper functions (PDF/image processing)
│── models/
│     └── best.pt          # Trained YOLO model weights
│── uploads/               # Temporary uploaded files
│── outputs/               # Processed output images
│── requirements.txt
│── README.md
Model Details
Architecture: YOLO (You Only Look Once)
Version: YOLOv5/YOLOv8 (depending on training setup)
Classes:
text
table
figure
Input size: 640×640 (standard training resolution)
Output: Bounding boxes with class labels and confidence scores

The model was trained on a custom dataset containing annotated document pages with structural elements.

Installation
1. Clone the repository
```bash
https://github.com/AnishaK00/Document-Analyzer-YOLO-.git
cd YOLO
```
2. Create virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
Running the Project

Start the Streamlit application:
```bash
streamlit run app.py
```

Then open in browser:

http://localhost:8501

Usage
1. Launch the application
2. Upload a document image or PDF
3. The system will:
 -Convert PDF pages to images (if applicable)
 -Run YOLO detection
 -Display annotated results
4. View detected text, tables, and figures with bounding boxes
   
Output Example
Input: Scanned document / research paper page
Output: Image with labeled bounding boxes around:
-Paragraphs (text)
-Tables
-Figures/diagrams

Future Improvements
1. Add OCR integration for text extraction
2. Improve table structure recognition (cell-level detection)
3. Export results as JSON/CSV
4. Multi-page PDF batch processing
5. Model upgrade to YOLOv8-seg for segmentation
