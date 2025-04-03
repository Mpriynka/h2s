#main.py
import streamlit as st
import requests
import pandas as pd
from session_manager import init_session_state, safe_get
from backend.utils import (
    extract_text_from_pdf, 
    extract_text_from_excel,
    process_audio
)
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from av import AudioFrame
import numpy as np
import io
import soundfile as sf

# Initialize session state
init_session_state()

# Configuration
BACKEND_URL = "http://localhost:8000"

def display_schedule(schedule_data):
    """Display schedule data in appropriate format"""
    if schedule_data is None:
        st.warning("No schedule data to display")
        return
        
    if isinstance(schedule_data, dict):
        if "schedule" in schedule_data:  # Timetable format
            df = pd.DataFrame(schedule_data["schedule"])
            st.table(df)
            if "breaks" in schedule_data:
                st.write("**Break Times:**")
                st.json(schedule_data["breaks"])
        else:  # Lesson plan format
            st.json(schedule_data)
    elif isinstance(schedule_data, list):
        st.table(pd.DataFrame(schedule_data))
    else:
        st.write(schedule_data)

def voice_recorder():
    ctx = webrtc_streamer(
        key="voice-recorder",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True},
    )
    
    if ctx.audio_receiver:
        st.info("Recording... Speak now")
        audio_frames = []
        while True:
            frame = ctx.audio_receiver.get_frame()
            if frame is None:
                break
            audio_frames.append(frame.to_ndarray())
        
        if audio_frames:
            audio_array = np.concatenate(audio_frames)
            wav_bytes = io.BytesIO()
            sf.write(wav_bytes, audio_array, samplerate=44100, format='WAV')
            text = process_audio(wav_bytes.getvalue())
            st.session_state.multi_input['voice'] = text
            st.success("Voice note captured!")

def handle_api_response(response):
    if response.status_code == 200:
        result = response.json()
        if result.get("status") == "success":
            st.session_state.current_schedule = result["schedule"]
            st.session_state.schedule_history.append(result["schedule"])
            return True
        else:
            st.error(f"Error: {result.get('message', 'Unknown error')}")
            if "raw_response" in result:
                st.text_area("Raw AI Response", result["raw_response"])
    else:
        st.error(f"API Error: {response.text}")
    return False

# Main UI
st.title("Teacher Scheduling Assistant")

# Schedule type selection
st.session_state.schedule_type = st.selectbox(
    "Select Schedule Type",
    ["weekly_timetable", "annual_lesson_plan", "monthly_lesson_plan", "weekly_lesson_plan"],
    index=0
)

# Document Upload
doc_file = st.file_uploader("Upload Reference Document", 
                          type=["pdf", "xlsx"],
                          help="Last year's timetable or lesson plan")

if doc_file:
    if doc_file.type == "application/pdf":
        doc_text = extract_text_from_pdf(doc_file.read())
    else:
        doc_text = extract_text_from_excel(doc_file.read())
    st.session_state.multi_input['document'] = doc_text

# Text Instructions
st.session_state.multi_input['text'] = st.text_area(
    "Modification Instructions",
    help="Describe what changes you want to make",
    value=safe_get('multi_input')['text']
)

# Voice Notes
st.subheader("Add Voice Notes")
voice_recorder()

# Generate Schedule
if st.button("Generate Schedule"):
    if not any(st.session_state.multi_input.values()):
        st.warning("Please provide at least one input source")
    else:
        with st.spinner("Creating your custom schedule..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate_with_context",
                    json={
                        "document_text": st.session_state.multi_input['document'],
                        "text_prompt": st.session_state.multi_input['text'],
                        "voice_transcript": st.session_state.multi_input['voice'],
                        "schedule_type": st.session_state.schedule_type,
                        "preferences": st.session_state.preferences
                    }
                )
                if handle_api_response(response):
                    st.session_state.multi_input['voice'] = ""  # Clear voice input
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

# Refinement Section - Only show if we have a current schedule
current_schedule = safe_get('current_schedule')
if current_schedule:
    st.header("Refinement Cycle")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Version")
        display_schedule(current_schedule)
    
    with col2:
        st.subheader("Make Changes")
        refine_method = st.radio("Refinement Method",
                               ["Text Instructions", "Voice Notes", "Both"],
                               horizontal=True)
        
        new_text = ""
        if refine_method in ["Text Instructions", "Both"]:
            new_text = st.text_area("Additional Instructions")
        
        if refine_method in ["Voice Notes", "Both"]:
            voice_recorder()
        
        if st.button("Apply Refinements"):
            feedback = {
                "text": new_text,
                "voice": st.session_state.multi_input['voice'],
                "current_schedule": current_schedule
            }
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/refine_schedule",
                    json=feedback
                )
                if handle_api_response(response):
                    st.session_state.multi_input['voice'] = ""
                    st.rerun()
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
else:
    st.info("Please generate a schedule first to enable refinement")