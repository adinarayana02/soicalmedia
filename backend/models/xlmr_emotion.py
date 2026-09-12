from __future__ import annotations

from functools import lru_cache
from typing import Dict, List

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from models.device import get_device


# XLM-RoBERTa emotion (pretrained)
# Note: this is a real HF model id; if you prefer a different XLM-R emotion checkpoint,
# set XLMR_EMOTION_MODEL_ID env var.
DEFAULT_MODEL_ID = "bhadresh-savani/xlm-roberta-base-emotion"


@lru_cache(maxsize=1)
def _load(model_id: str):
    device = get_device()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)
    model.eval()
    model.to(device)
    return device, tokenizer, model


def predict_emotions(text: str, top_k: int = 3) -> Dict:
    model_id = DEFAULT_MODEL_ID
    device, tokenizer, model = _load(model_id)

    with torch.inference_mode():
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        logits = model(**inputs).logits[0]
        probs = torch.softmax(logits, dim=-1).detach().cpu().numpy().tolist()

    id2label = model.config.id2label
    scores = {id2label[i].lower(): float(probs[i]) for i in range(len(probs))}
    sorted_items = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top_emotions = [k for k, _ in sorted_items[: max(1, top_k)]]
    return {"top_emotions": top_emotions, "scores": scores, "model_id": model_id}

