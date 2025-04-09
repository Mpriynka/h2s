# models.py
from enum import Enum
from typing import List, Dict
from pydantic import BaseModel

class QuestionType(str, Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    FILL_BLANKS = "fill_blanks"
    MATCH_FOLLOWING = "match_following"
    TRUE_FALSE = "true_false"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class BloomLevel(str, Enum):
    KNOWLEDGE = "knowledge"
    UNDERSTANDING = "understanding"
    APPLICATION = "application"
    ANALYSIS = "analysis"
    EVALUATION = "evaluation"
    CREATION = "creation"

class Question(BaseModel):
    text: str
    type: QuestionType
    options: List[str] = None
    answer: str
    bloom_level: BloomLevel
    difficulty: DifficultyLevel
    marks: int = 1

class TestPaper(BaseModel):
    subject: str
    topic: str
    grade: str
    questions: List[Question]
    total_marks: int