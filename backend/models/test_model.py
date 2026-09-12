import joblib
import pandas as pd
import os

def test_inference():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "behavior_model.pkl")
    
    print(f"Loading model from {MODEL_PATH}...")
    pipeline = joblib.load(MODEL_PATH)
    
    # Create a raw dummy input similar to actual data
    sample_data = pd.DataFrame([{
        "text_content": "Feeling really exhausted with all this constant scrolling...",
        "platform": "Instagram",
        "interaction_type": "post",
        "topic": "social_media",
        "emotion_label": "stress",
        "likes": 120,
        "comments_count": 45,
        "shares": 12,
        "session_duration": 45,
        "toxicity_score": 0.2,
        "avg_sentiment_score": -0.6,
        "posting_frequency": 2.5,
        "late_night_ratio": 0.8
    }])
    
    print("Running inference...")
    prediction = pipeline.predict(sample_data)
    print(f"Predicted Risk Label: {prediction[0]}")
    
    # Try probabilities if available
    try:
        probs = pipeline.predict_proba(sample_data)
        print(f"Prediction Probabilities: {dict(zip(pipeline.classes_, probs[0]))}")
    except Exception as e:
        print(f"No probabilities available: {e}")

if __name__ == "__main__":
    test_inference()
