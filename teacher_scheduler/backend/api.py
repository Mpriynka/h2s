from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from .models import ScheduleRequest, ScheduleResponse, InputMethod, DocumentType
from .scheduler import ScheduleGenerator
from .utils import extract_text_from_pdf, extract_text_from_excel, speech_to_text
import json
from typing import Optional

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

@app.post("/generate_schedule", response_model=ScheduleResponse)
async def generate_schedule(
    schedule_type: str = Form(...),
    input_method: str = Form(...),
    language: str = Form("english"),
    preferences: Optional[str] = Form(None),
    text_input: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    document_file: Optional[UploadFile] = File(None),
    document_type: Optional[str] = Form(None)
):
    try:
        # Process input based on input method
        input_content = ""
        if input_method == InputMethod.TEXT.value and text_input:
            input_content = text_input
        elif input_method == InputMethod.VOICE.value and audio_file:
            audio_bytes = await audio_file.read()
            input_content = speech_to_text(audio_bytes)
        elif input_method == InputMethod.DOCUMENT.value and document_file and document_type:
            doc_bytes = await document_file.read()
            if document_type == DocumentType.PDF.value:
                input_content = extract_text_from_pdf(doc_bytes)
            elif document_type == DocumentType.EXCEL.value:
                input_content = extract_text_from_excel(doc_bytes)
        
        # Parse preferences if provided
        pref_dict = json.loads(preferences) if preferences else {}
        
        request_data = {
            "schedule_type": schedule_type,
            "input_method": input_method,
            "input_content": input_content,
            "language": language,
            "preferences": pref_dict
        }
        
        # Generate schedule
        result = scheduler.generate_schedule(request_data)
        
        if result["status"] == "success":
            return ScheduleResponse(
                schedule=result["schedule"],
                message="Schedule generated successfully",
                status="success"
            )
        else:
            return ScheduleResponse(
                schedule={},
                message=result.get("message", "Error generating schedule"),
                status="error"
            )
            
    except Exception as e:
        return ScheduleResponse(
            schedule={},
            message=f"Error: {str(e)}",
            status="error"
        )

@app.post("/refine_schedule", response_model=ScheduleResponse)
async def refine_schedule(
    current_schedule: str = Form(...),
    feedback: str = Form(...)
):
    try:
        schedule_dict = json.loads(current_schedule)
        result = scheduler.refine_schedule(schedule_dict, feedback)
        
        if result["status"] == "success":
            return ScheduleResponse(
                schedule=result["schedule"],
                message="Schedule refined successfully",
                status="success"
            )
        else:
            return ScheduleResponse(
                schedule={},
                message=result.get("message", "Error refining schedule"),
                status="error"
            )
            
    except Exception as e:
        return ScheduleResponse(
            schedule={},
            message=f"Error: {str(e)}",
            status="error"
        )
