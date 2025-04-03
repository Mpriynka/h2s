#points/scheduler.py
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, Any
import json

class ScheduleGenerator:
    def __init__(self):
        self.llm = Ollama(model="llama2")
        self.parser = JsonOutputParser()
        
        self.prompt_templates = {
            "weekly_timetable": """You are an expert at creating school timetables. 
            Create a weekly timetable based on these requirements:
            {input}
            
            Preferences: {preferences}
            
            Structure your response as JSON with:
            - "days" (list of day names)
            - "periods" (list of periods per day)
            - "schedule" (dict mapping days to list of subjects/activities)
            - "breaks" (dict with break times)
            
            Example:
            {{
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "periods": ["Period 1", "Period 2", "Period 3", "Period 4"],
                "schedule": {{
                    "Monday": ["Math", "Science", "Break", "English"],
                    "Tuesday": ["History", "Geography", "Break", "Math"]
                }},
                "breaks": {{
                    "time": "11:00-11:30",
                    "after_period": 2
                }}
            }}
            """,
            
            "lesson_plan": """You are an expert at creating lesson plans. 
            Create a {plan_type} lesson plan based on:
            {input}
            
            Preferences: {preferences}
            
            Structure your response as JSON with:
            - "topics" (list of topics to cover)
            - "time_allocation" (dict with time estimates)
            - "teaching_methods" (list)
            - "assessments" (list)
            - "resources" (list)
            
            Example:
            {{
                "topics": ["Introduction to Algebra", "Linear Equations"],
                "time_allocation": {{
                    "total_weeks": 4,
                    "hours_per_week": 5
                }},
                "teaching_methods": ["Lecture", "Group Problem Solving"],
                "assessments": ["Weekly quizzes", "End-of-unit test"],
                "resources": ["Textbook Chapter 3", "Online practice problems"]
            }}
            """
        }
    
    def _clean_json_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from potentially messy AI response"""
        try:
            # Try parsing directly first
            return json.loads(response)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            if start_idx != -1 and end_idx != -1:
                try:
                    return json.loads(response[start_idx:end_idx+1])
                except json.JSONDecodeError:
                    pass
        return {"error": "Failed to parse response", "raw_response": response}
    
    def generate_schedule(self, request: Dict[str, Any]) -> Dict[str, Any]:
        schedule_type = request["schedule_type"]
        input_content = request["input_content"]
        preferences = request.get("preferences", {})
        
        if "timetable" in schedule_type:
            prompt_template = self.prompt_templates["weekly_timetable"]
            prompt = ChatPromptTemplate.from_template(prompt_template)
        else:
            plan_type = schedule_type.split("_")[0]
            prompt_template = self.prompt_templates["lesson_plan"]
            prompt = ChatPromptTemplate.from_template(prompt_template)
            input_content = f"Plan Type: {plan_type}\nRequirements: {input_content}"
        
        chain = prompt | self.llm | self.parser
        
        try:
            response = chain.invoke({
                "input": input_content,
                "preferences": json.dumps(preferences) if preferences else "None",
                "plan_type": plan_type if "lesson_plan" in schedule_type else ""
            })
            
            # Ensure we have a valid dictionary
            if isinstance(response, dict):
                return {"status": "success", "schedule": response}
            else:
                return {"status": "error", "message": "AI returned non-dict response", "raw_response": response}
                
        except Exception as e:
            return {"status": "error", "message": f"AI generation failed: {str(e)}"}
    
    def refine_schedule(self, current_schedule: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_template("""
        Refine this schedule based on teacher feedback. Only return valid JSON.
        
        Current Schedule:
        {current_schedule}
        
        Teacher Feedback:
        {feedback}
        
        Return the improved schedule in the same JSON format as the current one.
        """)
        
        chain = prompt | self.llm | self.parser
        
        try:
            response = chain.invoke({
                "current_schedule": json.dumps(current_schedule),
                "feedback": feedback
            })
            
            if isinstance(response, dict):
                return {"status": "success", "schedule": response}
            return {"status": "error", "message": "AI returned non-dict response", "raw_response": response}
            
        except Exception as e:
            return {"status": "error", "message": f"Refinement failed: {str(e)}"}
        


    def generate_with_context(self, document_text: str, text_prompt: str, 
                            voice_transcript: str, schedule_type: str, 
                            preferences: dict) -> Dict[str, Any]:
        """
        Generate schedule combining all input sources
        """
        combined_input = f"""
        REFERENCE DOCUMENT CONTENT:
        {document_text}
        
        TEXT INSTRUCTIONS:
        {text_prompt}
        
        VOICE NOTES:
        {voice_transcript}
        """
        
        prompt = ChatPromptTemplate.from_template("""
        Create a {schedule_type} using:
        1. This reference document: ||{document_text}||
        2. These text instructions: ||{text_prompt}||
        3. These voice notes: ||{voice_transcript}||
        
        Preferences: {preferences}
        
        Follow these rules:
        - Preserve useful structure from reference doc
        - Implement all text/voice instructions
        - Maintain consistent formatting
        - Return valid JSON only
        
        {format_instructions}
        """)
        
        chain = prompt | self.llm | self.parser
        return chain.invoke({
            "document_text": document_text,
            "text_prompt": text_prompt,
            "voice_transcript": voice_transcript,
            "preferences": preferences,
            "schedule_type": schedule_type,
            "format_instructions": self.parser.get_format_instructions()
        })