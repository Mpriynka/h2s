#logic/utils.py
import pdfplumber
import pandas as pd
from io import BytesIO
import speech_recognition as sr
from typing import Union
import soundfile as sf
import io
import numpy as np
from typing import Optional

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text content from PDF file"""
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    return text

def extract_text_from_excel(file_bytes: bytes) -> str:
    """Extract text content from Excel file"""
    df = pd.read_excel(BytesIO(file_bytes))
    return df.to_string()

def speech_to_text(audio_file: bytes) -> str:
    """Convert speech to text using Google's speech recognition"""
    recognizer = sr.Recognizer()
    with sr.AudioFile(BytesIO(audio_file)) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "API unavailable"

def format_schedule_as_table(schedule_data: dict) -> str:
    """Format schedule data as a markdown table"""
    if not schedule_data:
        return "No schedule data available"
    
    if isinstance(schedule_data, list):
        df = pd.DataFrame(schedule_data)
    else:
        df = pd.DataFrame.from_dict(schedule_data, orient='index')
    
    return df.to_markdown()

def process_audio_buffer(audio_buffer: bytes) -> Optional[bytes]:
    """Convert audio buffer to WAV format"""
    try:
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_buffer, dtype=np.int16)
        
        # Convert to WAV format in memory
        with io.BytesIO() as wav_buffer:
            sf.write(wav_buffer, audio_array, samplerate=16000, format='WAV')
            return wav_buffer.getvalue()
    except Exception as e:
        print(f"Audio processing error: {e}")
        return None

def process_audio(audio_bytes: bytes) -> str:
    """Convert processed audio bytes to text"""
    try:
        return speech_to_text(audio_bytes)
    except Exception as e:
        print(f"Audio processing error: {e}")
        return ""