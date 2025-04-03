from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict
import json
from .models import Question, QuestionType, DifficultyLevel, BloomLevel

class QuestionGenerator:
    def __init__(self):
        self.llm = Ollama(model="llama2")
        self.parser = JsonOutputParser()
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert educational test paper generator for Indian government schools.
            Generate exactly ONE question based on these requirements:
            - Subject: {subject}
            - Topic: {topic}
            - Grade: {grade}
            - Question Type: {question_type}
            - Difficulty: {difficulty}
            - Bloom's Level: {bloom_level}
            
            For MCQs: provide 4 options and mark the correct answer
            For fill-in-the-blanks: underline blanks like _____
            For match: provide 4 pairs
            For true/false: provide the correct answer
            
            Return ONLY this JSON structure:
            {{
                "question": "question text",
                "options": ["option1", "option2", ...] (only for MCQ/TrueFalse/Match),
                "answer": "correct answer",
                "explanation": "brief explanation" (optional)
            }}
            """),
            ("human", "Generate a {question_type} question about {topic} in {subject} for grade {grade}")
        ])
        
        self.chain = self.prompt_template | self.llm | self.parser
        
    def generate(self, subject: str, topic: str, grade: str, 
                question_types: List[str], num_questions: int,
                difficulty_dist: Dict[str, float], 
                bloom_dist: Dict[str, float],
                context: str = None) -> List[dict]:
        
        questions = []
        for q_type in question_types:
            num = num_questions // len(question_types)
            for _ in range(num):
                difficulty = self._select_from_distribution(difficulty_dist)
                bloom_level = self._select_from_distribution(bloom_dist)
                
                try:
                    response = self.chain.invoke({
                        "subject": subject,
                        "topic": topic,
                        "grade": grade,
                        "question_type": q_type,
                        "difficulty": difficulty,
                        "bloom_level": bloom_level,
                        "context": context or ""
                    })
                    
                    # Validate response structure
                    if not isinstance(response, dict):
                        raise ValueError("Invalid response format")
                    
                    questions.append({
                        "text": response.get("question", f"Question about {topic}"),
                        "type": q_type,
                        "options": response.get("options", []),
                        "answer": response.get("answer", "Answer not provided"),
                        "bloom_level": bloom_level,
                        "difficulty": difficulty,
                        "marks": self._calculate_marks(difficulty, bloom_level)
                    })
                except Exception as e:
                    print(f"Error generating question: {e}")
                    # Fallback question
                    questions.append(self._create_fallback_question(
                        subject, topic, q_type, difficulty, bloom_level
                    ))
        
        return questions
    
    def _create_fallback_question(self, subject, topic, q_type, difficulty, bloom_level):
        """Create a simple fallback question when generation fails"""
        base_question = f"Explain {topic} in {subject}"
        if q_type == "mcq":
            base_question = f"Which of these relates to {topic} in {subject}?"
            return {
                "text": base_question,
                "type": q_type,
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "answer": "Option 1",
                "bloom_level": bloom_level,
                "difficulty": difficulty,
                "marks": 1
            }
        return {
            "text": base_question,
            "type": q_type,
            "answer": f"Sample answer about {topic}",
            "bloom_level": bloom_level,
            "difficulty": difficulty,
            "marks": 1 if difficulty == "easy" else 2
        }
    
    def _select_from_distribution(self, distribution: Dict[str, float]) -> str:
        import random
        return random.choices(
            list(distribution.keys()), 
            weights=list(distribution.values())
        )[0]
    
    def _calculate_marks(self, difficulty: str, bloom_level: str) -> int:
        base = 1
        if difficulty == "medium": base += 0.5
        elif difficulty == "hard": base += 1
        if bloom_level in ["application", "analysis"]: base += 0.5
        elif bloom_level in ["evaluation", "creation"]: base += 1
        return max(1, round(base))