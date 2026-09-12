from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import torch
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

from models.device import get_device


MODEL_ID = "Salesforce/blip-image-captioning-base"


@lru_cache(maxsize=1)
def _load():
    device = get_device()
    processor = BlipProcessor.from_pretrained(MODEL_ID)
    model = BlipForConditionalGeneration.from_pretrained(MODEL_ID)
    model.eval()
    model.to(device)
    return device, processor, model


def caption_image(image_path: Path) -> str:
    device, processor, model = _load()
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=40)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption.strip()

