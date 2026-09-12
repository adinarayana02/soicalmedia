import torch
from typing import Dict, Any

MODEL_ID = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
_tokenizer = None
_model = None
_model_failed = False

def get_text_analyzer():
    global _tokenizer, _model, _model_failed
    if _model_failed:
        return None, None

    if _tokenizer is None or _model is None:
        try:
            print("Loading XLM-RoBERTa text model with safetensors...")
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=False)
            try:
                _model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID, use_safetensors=True)
            except Exception:
                _model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
            _model.eval()
            print("XLM-RoBERTa model successfully loaded.")
        except Exception as e:
            print(f"[TextModel] Transformers model load deferred ({e}). Using rule-based sentiment engine.")
            _model_failed = True
            return None, None

    return _tokenizer, _model

def analyze_text(text: str) -> Dict[str, Any]:
    if not text or not text.strip():
        return {"sentiment": "neutral", "emotions": [], "toxicity": 0.0, "emotional_intensity": 0.0, "scores": {"neutral": 1.0}}

    tokenizer, model = get_text_analyzer()

    if tokenizer is not None and model is not None:
        try:
            with torch.inference_mode():
                inputs = tokenizer(text[:512], return_tensors="pt", truncation=True, max_length=512)
                logits = model(**inputs).logits[0]
                probs = torch.softmax(logits, dim=-1).detach().cpu().numpy().tolist()

            id2label = getattr(model.config, "id2label", {0: "negative", 1: "neutral", 2: "positive"})
            scores = {id2label[i].lower(): float(probs[i]) for i in range(len(probs))}
            
            neg_score = scores.get('negative', 0.0)
            pos_score = scores.get('positive', 0.0)
            neutral_score = scores.get('neutral', 0.0)

            emotions = []
            if neg_score > 0.4: emotions.append("frustration")
            if pos_score > 0.6: emotions.append("joy")
            
            toxic_triggers = ["hate", "bitch", "fuck", "kill", "shut up", "idiot", "stupid", "dumb", "ugly"]
            text_lower = text.lower()
            base_toxicity = neg_score if neg_score > 0.6 else 0.0
            if any(t in text_lower for t in toxic_triggers):
                base_toxicity = min(1.0, base_toxicity + 0.3)
                
            predicted = max(scores.items(), key=lambda x: x[1])[0]
            
            return {
                "sentiment": predicted,
                "emotions": emotions,
                "toxicity": base_toxicity,
                "emotional_intensity": 1.0 - neutral_score,
                "scores": scores
            }
        except Exception as e:
            print(f"[TextModel] Model inference error ({e}), falling back to heuristic engine.")

    # Rule-Based Heuristic Fallback Analysis Engine
    text_lower = text.lower()
    pos_words = {"good", "great", "happy", "awesome", "love", "nice", "excellent", "best", "like", "wonderful", "enjoy", "thanks", "thank"}
    neg_words = {"bad", "terrible", "hate", "sad", "angry", "worst", "horrible", "annoying", "fail", "hurt", "kill", "stupid"}
    toxic_words = {"hate", "bitch", "fuck", "kill", "shut up", "idiot", "stupid", "dumb", "ugly"}

    words = set(text_lower.split())
    pos_matches = len(words.intersection(pos_words))
    neg_matches = len(words.intersection(neg_words))
    toxic_matches = len(words.intersection(toxic_words))

    if pos_matches > neg_matches:
        predicted = "positive"
        scores = {"positive": 0.8, "neutral": 0.15, "negative": 0.05}
        emotions = ["joy"]
    elif neg_matches > pos_matches:
        predicted = "negative"
        scores = {"positive": 0.05, "neutral": 0.15, "negative": 0.8}
        emotions = ["frustration"]
    else:
        predicted = "neutral"
        scores = {"positive": 0.2, "neutral": 0.6, "negative": 0.2}
        emotions = []

    toxicity = min(1.0, toxic_matches * 0.4)

    return {
        "sentiment": predicted,
        "emotions": emotions,
        "toxicity": toxicity,
        "emotional_intensity": 0.5 if (pos_matches or neg_matches) else 0.1,
        "scores": scores
    }
