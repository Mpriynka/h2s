# api/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import List, Optional
import os
from .question_generator import QuestionGenerator
from .syllabus_mapping import SyllabusMapper

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
question_gen = QuestionGenerator()
syllabus_mapper = SyllabusMapper()


class TopicRequest(BaseModel):
    subject: str
    grade: str

class QuestionRequest(BaseModel):
    subject: str
    topic: str
    grade: str
    question_types: List[str]
    num_questions: int
    difficulty_dist: dict
    bloom_dist: dict
    context: Optional[str] = None

@app.post("/suggest-topics")
async def suggest_topics(request: TopicRequest):
    try:
        topics = syllabus_mapper.get_related_topics(request.subject, request.grade)
        return {"topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-questions")
async def generate_questions(request: QuestionRequest):
    try:
        questions = question_gen.generate(
            subject=request.subject,
            topic=request.topic,
            grade=request.grade,
            question_types=request.question_types,
            num_questions=request.num_questions,
            difficulty_dist=request.difficulty_dist,
            bloom_dist=request.bloom_dist,
            context=request.context
        )
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))