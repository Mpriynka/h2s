# api/question_generator.py
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict
import json
import requests
from .models import Question, QuestionType, DifficultyLevel, BloomLevel

class RAGClient:
    def __init__(self, backend_url: str = "http://localhost:8001"):
        self.backend_url = backend_url
    
    def get_context(self, query: str, top_k: int = 3) -> str:
        """Query the knowledge base and return relevant context"""
        try:
            response = requests.post(
                f"{self.backend_url}/query/",
                json={"text": query, "top_k": top_k}
            )
            if response.status_code == 200:
                result = response.json()
                if result["results"]["source_documents"]:
                    # Combine the context from all relevant documents
                    context = "\n\n".join(
                        f"Source: {doc['source']}, Page: {doc.get('page', 'N/A')}\n"
                        f"Content: {doc.get('text', '')}"
                        for doc in result["results"]["source_documents"]
                    )
                    return context
        except Exception as e:
            print(f"Error querying knowledge base: {str(e)}")
        return None


class QuestionGenerator:
    def __init__(self):
        self.llm = Ollama(model="llama2")
        self.parser = JsonOutputParser()
        self.rag_client = RAGClient()
        
        self.batch_prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert educational test paper generator for Indian government schools.
            Generate EXACTLY {num_questions} UNIQUE questions of type {question_type} based on:
            - Subject: {subject}
            - Topic: {topic}
            - Grade: {grade}
            - Difficulty distribution: {difficulty_dist}
            - Bloom's taxonomy distribution: {bloom_dist}
            
            Rules:
            1. Ensure ALL questions are DISTINCT and cover different aspects
            2. Vary question phrasing and focus areas
            3. For MCQs: provide 4 options per question
            4. For fill-in-the-blanks: underline blanks like _____
            5. For match: provide 4 pairs per question
            6. For true/false: provide the correct answer
            
            Return ONLY this JSON structure:
            {{
                "questions": [
                    {{
                        "question": "question text",
                        "type": "{question_type}",
                        "difficulty": "easy/medium/hard",
                        "bloom_level": "remember/understand/etc",
                        "options": ["option1", ...]  // if applicable
                    }},
                    // more questions...
                ]
            }}
            """),
            ("human", "Generate {num_questions} {question_type} questions about {topic} in {subject} for grade {grade}")
        ])
        
        self.batch_chain = self.batch_prompt_template | self.llm | self.parser

    def generate(self, subject: str, topic: str, grade: str, 
                question_types: List[str], num_questions: int,
                difficulty_dist: Dict[str, float], 
                bloom_dist: Dict[str, float],
                context: str = None) -> List[dict]:
        
        # Get context once at the beginning
        rag_context = context or self.rag_client.get_context(
            f"{subject} {topic} for grade {grade}"
        ) or ""
        print("📝📝📝📝📝📝📝📝📝📝📝", rag_context)
        
        questions = []
        for q_type in question_types:
            num = num_questions // len(question_types)
            if num < 1:
                num = 1
                
            try:
                # Generate all questions of this type in one batch
                response = self.batch_chain.invoke({
                    "subject": subject,
                    "topic": topic,
                    "grade": grade,
                    "question_type": q_type,
                    "num_questions": num,
                    "difficulty_dist": difficulty_dist,
                    "bloom_dist": bloom_dist,
                    "context": rag_context
                })
                
                if not isinstance(response, dict) or "questions" not in response:
                    raise ValueError("Invalid response format")
                
                for q in response["questions"]:
                    questions.append({
                        "text": q.get("question", f"Question about {topic}"),
                        "type": q_type,
                        "options": q.get("options", []),
                        "bloom_level": q.get("bloom_level", 
                            self._select_from_distribution(bloom_dist)),
                        "difficulty": q.get("difficulty",
                            self._select_from_distribution(difficulty_dist)),
                        "marks": self._calculate_marks(
                            q.get("difficulty", "easy"),
                            q.get("bloom_level", "remember"))
                    })
                    
            except Exception as e:
                print(f"Error batch generating {q_type} questions: {e}")
                # Fallback to individual generation if batch fails
                questions.extend(self._generate_individual_questions(
                    subject, topic, grade, q_type, num,
                    difficulty_dist, bloom_dist, rag_context
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

    def _generate_individual_questions(self, subject, topic, grade, q_type, num,
                                     difficulty_dist, bloom_dist, context):
        """Fallback method for individual question generation"""
        questions = []
        existing_questions = set()
        
        while len(questions) < num:
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
                    "context": context
                })
                
                if not isinstance(response, dict):
                    continue
                    
                question_text = response.get("question")
                if question_text and question_text not in existing_questions:
                    existing_questions.add(question_text)
                    questions.append({
                        "text": question_text,
                        "type": q_type,
                        "options": response.get("options", []),
                        "bloom_level": bloom_level,
                        "difficulty": difficulty,
                        "marks": self._calculate_marks(difficulty, bloom_level)
                    })
            except Exception as e:
                print(f"Error generating individual question: {e}")
                questions.append(self._create_fallback_question(
                    subject, topic, q_type, difficulty, bloom_level
                ))
                if len(questions) >= num:
                    break
        
        return questions
    
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