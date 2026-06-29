from pdf2image import convert_from_path
from PIL import Image
import os


def convert_pdf_to_images(pdf_path):
    """
    Convert a PDF file to a list of PIL Image objects.
    """
    return convert_from_path(pdf_path, dpi=200, poppler_path="/opt/homebrew/bin")

def extract_detected_regions(image: Image.Image, detections, label_map):

    regions = []
    for det in detections:
        x1, y1, x2, y2, conf, cls = det

        # Convert float coordinates to integers for cropping
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        # Crop the region from the image
        cropped = image.crop((x1, y1, x2, y2))

        # Get label string from label_map, default to 'unknown' if cls not found
        label = label_map.get(cls, "unknown")

        regions.append({
            "label": label,
            "image": cropped
        })
    return regions


def save_combined_regions(regions, save_dir="output"):
    os.makedirs(save_dir, exist_ok=True)

    buckets = {"text": [], "table": [], "figure": []}

    for region in regions:
        buckets[region["label"]].append(region["image"])

    for label, imgs in buckets.items():
        if not imgs:
            continue

        max_width = max(img.width for img in imgs)
        total_height = sum(img.height for img in imgs)

        combined_img = Image.new("RGB", (max_width, total_height), color=(255, 255, 255))

        y_offset = 0
        for img in imgs:
            combined_img.paste(img, (0, y_offset))
            y_offset += img.height

        combined_img.save(os.path.join(save_dir, f"{label}.png"))