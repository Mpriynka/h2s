import os

class Config:
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    AUDIO_SAMPLE_RATE = 16000