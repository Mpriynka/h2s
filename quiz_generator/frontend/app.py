import streamlit as st
import requests
from typing import List, Dict
import json
from pathlib import Path
import os

# Configuration
BACKEND_URL = "http://localhost:8000"  # Update with your FastAPI URL
SUBJECTS = ["Mathematics", "Science", "Social Studies", "English", "Hindi"]
GRADES = ["5", "6", "7", "8"]

def initialize_session_state():
    """Initialize all required session state variables"""
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "context" not in st.session_state:
        st.session_state.context = ""
    if "subject" not in st.session_state:
        st.session_state.subject = SUBJECTS[0]
    if "grade" not in st.session_state:
        st.session_state.grade = GRADES[0]
    if "suggested_topics" not in st.session_state:
        st.session_state.suggested_topics = []

def main():
    st.set_page_config(page_title="Test Paper Generator", layout="wide")
    initialize_session_state()
    
    st.title("📝 AI Test Paper Generator for Government Teachers")
    st.markdown("Create customized test papers aligned with Indian curriculum standards")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Test Configuration")
        
        # Subject and Grade selection
        st.session_state.subject = st.selectbox(
            "Subject", 
            SUBJECTS,
            index=SUBJECTS.index(st.session_state.subject)
        )
        
        st.session_state.grade = st.selectbox(
            "Grade", 
            GRADES,
            index=GRADES.index(st.session_state.grade)
        )
        
        # Get suggested topics
        if st.button("Get Suggested Topics"):
            response = requests.post(
                f"{BACKEND_URL}/suggest-topics",
                json={
                    "subject": st.session_state.subject, 
                    "grade": st.session_state.grade
                }
            )
            if response.status_code == 200:
                st.session_state.suggested_topics = response.json()["topics"]
            else:
                st.error("Failed to get suggested topics")
        
        # Topic selection
        topic = st.text_input("Topic", help="Enter a topic or select from suggestions")
        if st.session_state.suggested_topics:
            st.write("Suggested Topics:")
            for t in st.session_state.suggested_topics:
                if st.button(t, key=f"topic_{t}"):
                    topic = t
        
        # Question types
        question_types = st.multiselect(
            "Question Types",
            ["MCQ", "Short Answer", "Long Answer", "Fill in the Blanks", "Match the Following", "True/False"],
            default=["MCQ", "Short Answer"]
        )
        
        # Number of questions
        num_questions = st.slider("Number of Questions", 5, 50, 10)
        
        # Difficulty distribution
        st.subheader("Difficulty Distribution")
        easy = st.slider("Easy (%)", 0, 100, 40)
        medium = st.slider("Medium (%)", 0, 100, 40)
        hard = 100 - easy - medium
        st.write(f"Hard: {hard}%")
        
        # Bloom's Taxonomy
        st.subheader("Bloom's Taxonomy")
        knowledge = st.slider("Remembering (%)", 0, 100, 30)
        understanding = st.slider("Understanding (%)", 0, 100, 40)
        application = st.slider("Applying (%)", 0, 100, 20)
        analysis = st.slider("Analyzing (%)", 0, 100, 5)
        evaluation = st.slider("Evaluating (%)", 0, 100, 3)
        creation = 100 - knowledge - understanding - application - analysis - evaluation
        st.write(f"Creating: {creation}%")
    
    # Generate button
    if st.button("Generate Test Paper", type="primary"):
        if not topic:
            st.error("Please enter a topic")
            return
            
        difficulty_dist = {
            "easy": easy/100,
            "medium": medium/100,
            "hard": hard/100
        }
        
        bloom_dist = {
            "knowledge": knowledge/100,
            "understanding": understanding/100,
            "application": application/100,
            "analysis": analysis/100,
            "evaluation": evaluation/100,
            "creation": creation/100
        }
        
        payload = {
            "subject": st.session_state.subject,
            "topic": topic,
            "grade": st.session_state.grade,
            "question_types": [q.lower().replace(" ", "_") for q in question_types],
            "num_questions": num_questions,
            "difficulty_dist": difficulty_dist,
            "bloom_dist": bloom_dist,
            "context": st.session_state.context
        }
        
        with st.spinner("Generating questions..."):
            response = requests.post(
                f"{BACKEND_URL}/generate-questions",
                json=payload
            )
            
            if response.status_code == 200:
                st.session_state.questions = response.json()["questions"]
                st.success("Test paper generated successfully!")
            else:
                st.error(f"Failed to generate questions: {response.text}")
    
    # Display generated questions
    if st.session_state.questions:
        st.header("Generated Test Paper")
        st.subheader(f"{st.session_state.subject} - {topic} (Grade {st.session_state.grade})")
        
        total_marks = sum(q.get("marks", 1) for q in st.session_state.questions)
        st.write(f"Total Marks: {total_marks}")
        
        for i, q in enumerate(st.session_state.questions, 1):
            st.markdown(f"**Q{i}. {q['text']}** ({q['marks']} mark(s))")
            
            if q["type"] in ["mcq", "true_false", "match_following"] and q.get("options"):
                for j, opt in enumerate(q["options"], 1):
                    st.write(f"   {j}. {opt}")
            
            if q["type"] == "fill_blanks":
                st.write("__________________________")
            st.caption(f"Difficulty: {q['difficulty'].title()} | Bloom's Level: {q['bloom_level'].title()}")
            
            st.write("---")
        
        # Download options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download as JSON",
                data=json.dumps(st.session_state.questions, indent=2),
                file_name=f"{st.session_state.subject}_{topic}_test.json",
                mime="application/json"
            )
        with col2:
            st.download_button(
                label="Download as Text",
                data="\n".join(
                    f"Q{i+1}. {q['text']}\n\n" 
                    for i, q in enumerate(st.session_state.questions)
                ),
                file_name=f"{st.session_state.subject}_{topic}_test.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()