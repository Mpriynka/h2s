import os
from pathlib import Path

class Config:
    # Ollama Configuration
    OLLAMA_MODEL = "llama2"
    OLLAMA_BASE_URL = "http://localhost:11434"
    
    # FastAPI Configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    
    # File Storage
    UPLOAD_FOLDER = Path("uploads")
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    
    # Supported Languages
    LANGUAGES = {
        'en': 'English',
        'hi': 'Hindi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'bn': 'Bengali',
        'mr': 'Marathi'
    }