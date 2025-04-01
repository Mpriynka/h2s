from pydantic import BaseModel
from typing import Optional, List, Dict, Union
from enum import Enum

class ScheduleType(str, Enum):
    WEEKLY_TIMETABLE = "weekly_timetable"
    ANNUAL_LESSON_PLAN = "annual_lesson_plan"
    MONTHLY_LESSON_PLAN = "monthly_lesson_plan"
    WEEKLY_LESSON_PLAN = "weekly_lesson_plan"

class InputMethod(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    DOCUMENT = "document"

class DocumentType(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"

class ScheduleRequest(BaseModel):
    schedule_type: ScheduleType
    input_method: InputMethod
    input_content: str
    document_type: Optional[DocumentType] = None
    language: str = "english"
    preferences: Optional[Dict[str, Union[str, List[str]]]] = None

class ScheduleResponse(BaseModel):
    schedule: Dict[str, Union[str, List, Dict]]
    message: str
    status: str
