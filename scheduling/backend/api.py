#backend/api.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from .scheduler import ScheduleGenerator
from .utils import extract_text_from_pdf, extract_text_from_excel, speech_to_text
import json
from typing import Optional
from fastapi import Request 

app = FastAPI(title="Teacher Scheduling Assistant API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = ScheduleGenerator()

@app.post("/generate_with_context")
async def generate_with_context(request: Request):
    data = await request.json()
    result = scheduler.generate_with_context(
        document_text=data.get('document_text', ''),
        text_prompt=data.get('text_prompt', ''),
        voice_transcript=data.get('voice_transcript', ''),
        schedule_type=data.get('schedule_type', 'weekly_timetable'),
        preferences=data.get('preferences', {})
    )
    return result

@app.post("/refine_schedule")
async def refine_schedule(request: Request):
    data = await request.json()
    result = scheduler.refine_schedule(
        current_schedule=data['current_schedule'],
        text_feedback=data.get('text', ''),
        voice_feedback=data.get('voice', '')
    )
    return result


@app.post("/process_audio")
async def process_audio_endpoint(audio_file: UploadFile = File(...)):
    audio_bytes = await audio_file.read()
    processed = process_audio_buffer(audio_bytes)
    if processed:
        text = speech_to_text(processed)
        return {"text": text}
    return {"error": "Audio processing failed"}