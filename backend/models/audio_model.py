from transformers import pipeline

_whisper_pipeline = None

def get_audio_model():
    global _whisper_pipeline
    if _whisper_pipeline is None:
        print("Loading Whisper tiny model...")
        _whisper_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")
    return _whisper_pipeline

def analyze_audio(audio_bytes: bytes) -> str:
    """Takes audio bytes and converts to text via Whisper."""
    try:
        transcriber = get_audio_model()
        # The pipeline accepts raw bytes
        result = transcriber(audio_bytes)
        return result.get("text", "")
    except Exception as e:
        print(f"Error processing audio: {e}")
        return ""
