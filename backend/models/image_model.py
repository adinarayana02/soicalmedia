import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import io

_processor = None
_model = None

def get_image_model():
    global _processor, _model
    if _processor is None or _model is None:
        print("Loading BLIP image captioning model...")
        # Load models once globally
        _processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        _model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return _processor, _model

def analyze_image(image_bytes: bytes) -> str:
    """Returns a textual caption describing the behavior or context in the image."""
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        processor, model = get_image_model()
        
        inputs = processor(image, return_tensors="pt")
        
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        print(f"Error processing image: {e}")
        return ""
