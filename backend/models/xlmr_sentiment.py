from __future__ import annotations

from functools import lru_cache
from typing import Dict

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from models.device import get_device


# XLM-RoBERTa sentiment (pretrained)
# Widely used multilingual sentiment model based on XLM-R.
MODEL_ID = "cardiffnlp/twitter-xlm-roberta-base-sentiment"


@lru_cache(maxsize=1)
def _load():
    device = get_device()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
    model.eval()
    model.to(device)
    return device, tokenizer, model


def predict_sentiment(text: str) -> Dict:
    device, tokenizer, model = _load()
    with torch.inference_mode():
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        logits = model(**inputs).logits[0]
        probs = torch.softmax(logits, dim=-1).detach().cpu().numpy().tolist()

    # Model uses labels: negative, neutral, positive (3-way)
    id2label = model.config.id2label
    scores = {id2label[i].lower(): float(probs[i]) for i in range(len(probs))}
    label = max(scores, key=scores.get)
    return {"label": label, "scores": scores, "model_id": MODEL_ID}

