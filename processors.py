import pytesseract
from io import BytesIO
from PIL import Image, ImageOps, ImageFilter
from img2table.document import Image as TableImg
from img2table.ocr import TesseractOCR
import streamlit as st

def extract_text(crop: Image.Image) -> str:
    """extract text from a cropped doc region using OCR-using tesseract"""
    
    #convert to grayscale
    processed  = ImageOps.grayscale(crop)
    
    #improve contrast 
    processed = ImageOps.autocontrast(processed)
    
    #reduce small noise
    processed = processed.filter(ImageFilter.MedianFilter(size=3))
    
    #OCR
    text = pytesseract.image_to_string(processed, lang="eng", config="--psm 6")
    
    return text.strip()

def extract_tables(crop: Image.Image) -> list:
    "detect  table structure and extract its cells"
    
    buffer = BytesIO()
    crop.convert("RGB").save(buffer, format="PNG")
    buffer.seek(0)
    
    document = TableImg(src=buffer)
    ocr = TesseractOCR(n_threads=1, lang="eng")
    
    tables = document.extract_tables(ocr=ocr,
                                     implicit_rows=True,
                                     implicit_columns=True,
                                     borderless_tables=False,
                                     min_confidence=50,
                                     max_workers=1
                                    )
    #return each extracted table as pandas dataframe
    return [
        table.df
        for table in tables
        if table.df is not None and not table.df.empty
    ]
    
def analyze_figure(crop: Image.Image) -> dict:
    width, height = crop.size
    embedded_text = extract_text(crop)
    
    if width > height:
        orientation = "Landscape"
    elif height > width:
        orientation = "Portrait"
    else:
        orientation = "Square"
        
    return {
        "width": width,
        "height": height,
        "aspect_ratio": round(width/height, 2) if height else 0,
        "orientation": orientation,
        "embedded_text": embedded_text
        
    }

@st.cache_data(show_spinner=False)
def process_selected_crop(crop: Image.Image, label: str) -> dict:
    "route a selected crop to its appropriate processor"
    try:
        if label == "text":
            return {
                "type": "text",
                "result": extract_text(crop)
            }
        elif label == "table":
            return {
                "type": "table",
                "result": extract_tables(crop)
            }
        elif label == "figure":
            return {
                "type": "figure",
                "result": analyze_figure(crop)
            }

        return {
            "type": "unknwon",
            "result": None,
            "error": "Unsupported region class."
        }
    
    except Exception as error:
        return {
            "type": label,
            "result": None,
            "error": str(error)
        }