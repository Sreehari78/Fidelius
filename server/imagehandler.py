from presidio_image_redactor import ImageRedactorEngine, ImageAnalyzerEngine
from PIL import Image
import os
import pytesseract

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def predict_image_entities(file_path):
    """
    Predict PII entities in an image using Presidio Image Redactor.
    
    Args:
        file_path (str): Path to the input image
    
    Returns:
        list: List of detected PII entity types
    
    Raises:
        FileNotFoundError: If the image file doesn't exist
        Exception: For other errors during processing
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")
        
    try:
        # Initialize the analyzer engine first
        analyzer_engine = ImageAnalyzerEngine()
        
        # Open the image
        with Image.open(file_path) as img:
            # Analyze the image to detect PII entities
            analysis_results = analyzer_engine.analyze(img)
            
            # Extract unique entity types from the analysis
            entities = {result.entity_type for result in analysis_results}
            
            return list(entities)
    
    except Exception as e:
        raise Exception(f"Error predicting image entities: {str(e)}")

def redact_image(file_path, entities_to_redact=None, fill_color=(255, 192, 203)):
    """
    Redact sensitive information from an image using Presidio Image Redactor.
    
    Args:
        file_path (str): Path to the input image
        entities_to_redact (list): Optional list of specific PII entities to redact
        fill_color (tuple): RGB tuple for the redaction fill color (default: pink)
    
    Returns:
        str: Path to the redacted image
    
    Raises:
        FileNotFoundError: If the image file doesn't exist
        Exception: For other errors during processing
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")
        
    try:
        # Initialize both analyzer and redactor engines
        analyzer_engine = ImageAnalyzerEngine()
        engine = ImageRedactorEngine(image_analyzer_engine=analyzer_engine)
        
        # Open the image using PIL
        with Image.open(file_path) as image:
            # Redact the image with the specified fill color and entities
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
            
            # Generate output path in the same directory as input
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_dir = os.path.dirname(file_path)
            output_path = os.path.join(
                output_dir,
                f"{base_name}_redacted.png"
            )
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Save the redacted image
            redacted_image.save(output_path, "PNG")
            
        return output_path
    
    except Exception as e:
        raise Exception(f"Error redacting image: {str(e)}")
