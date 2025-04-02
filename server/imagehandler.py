from presidio_image_redactor import ImageRedactorEngine, ImageAnalyzerEngine
from PIL import Image, ImageDraw, ImageFont
import os
import pytesseract
import difflib
import shutil
import easyocr
from chat import chatlocal
from pydantic import BaseModel

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#EastOCR model loader
def load_model():
    reader= easyocr.Reader(['en'])
    return reader


# Header Detection Functionality 
def predict_image_entities(file_path):
    """
    Predict PII entities in an image using Presidio Image Redactor.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")
        
    try:
        analyzer_engine = ImageAnalyzerEngine()
        
        with Image.open(file_path) as img:
            analysis_results = analyzer_engine.analyze(img)
            entities = {result.entity_type for result in analysis_results}
            
            return list(entities)
    
    except Exception as e:
        raise Exception(f"Error predicting image entities: {str(e)}")


#Redaction Functionality
def redact_image(file_path,entities_to_redact=None, fill_color=(255,192,203)):
    """
    Redact sensitive information from an image using Presidio Image Redactor.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")
    try:
        analyzer_engine = ImageAnalyzerEngine()
        engine = ImageRedactorEngine(image_analyzer_engine = analyzer_engine)

        with Image.open(file_path) as image:
            if entities_to_redact:
                redacted_image = engine.redact(
                    image=image,
                    fill=fill_color,
                    entities=entities_to_redact
                )
            else:
                redacted_image = engine.redact(
                    image=image,
                    fill=fill_color
                )
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_dir = os.path.dirname(file_path)
            output_path = os.path.join(output_dir, f"{base_name}_redacted.png")
            os.makedirs(output_dir, exist_ok=True)
            redacted_image.save(output_path,"PNG")

        return output_path
    except Exception as e:
        raise Exception(f"Error redacting image: {str(e)}")

# Obfuscation Functionality
def obfuscate_image(json_data, reader):
    """
    Obfuscate sensitive information in an image.
    """
    file_path = json_data.get('filePath')
    output_path = json_data.get('outputPath', file_path)
    headers = json_data.get('headers')

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")
    print("File path:", file_path)
    print("Output path:", output_path)
    text_list = [header['name'] for header in headers if header['mode'] == 'obfuscate']
    replacement_list = [header['prompt'] for header in headers if header['mode'] == 'obfuscate']
    print("Text list:", text_list)
    print("Replacement list:", replacement_list)
    if not text_list or not replacement_list:
        raise ValueError("No obfuscation instructions provided")

    try:
        font = ImageFont.truetype(r"C:\\Windows\\Fonts\\Arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()

    img = Image.open(file_path)
    draw = ImageDraw.Draw(img)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    n_boxes = len(data['level'])

    for i in range(n_boxes):
        word = data['text'][i].strip()
        matches = difflib.get_close_matches(word, text_list, n=1, cutoff=0.6)
        if matches:
            candidate = matches[0]
            idx = text_list.index(candidate)
            replacement = replacement_list[idx]
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            draw.rectangle([x, y, x + w, y + h], fill="white")
            bbox = draw.textbbox((0, 0), replacement, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = x + (w - text_width) / 2
            text_y = y + (h - text_height) / 2
            draw.text((text_x, text_y), replacement, fill="black", font=font)

    img.save(output_path)
    return output_path