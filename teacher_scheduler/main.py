import streamlit as st
import requests
import json
import pandas as pd
from io import BytesIO
from PIL import Image
import time

# Configuration
BACKEND_URL = "http://localhost:8000"  # Update if your FastAPI server is elsewhere

# Initialize session state
if 'current_schedule' not in st.session_state:
    st.session_state.current_schedule = None
if 'schedule_history' not in st.session_state:
    st.session_state.schedule_history = []

# Helper functions
def display_schedule(schedule_data):
    """Display schedule data in appropriate format"""
    if not schedule_data:
        st.warning("No schedule data to display")
        return
    
    if isinstance(schedule_data, dict):
        if all(isinstance(k, str) and isinstance(v, (list, dict)) for k, v in schedule_data.items()):
            # Likely a timetable structure
            df = pd.DataFrame.from_dict(schedule_data, orient='index')
            st.table(df)
        else:
            # Likely a lesson plan
            st.json(schedule_data)
    elif isinstance(schedule_data, list):
        df = pd.DataFrame(schedule_data)
        st.table(df)
    else:
        st.write(schedule_data)

def save_to_file(data, file_type='json'):
    """Convert data to downloadable file"""
    if file_type == 'json':
        file_data = json.dumps(data, indent=2)
        file_ext = "json"
    elif file_type == 'excel':
        if isinstance(data, dict):
            df = pd.DataFrame.from_dict(data, orient='index')
        else:
            df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=True)
        file_data = output.getvalue()
        file_ext = "xlsx"
    return file_data, file_ext

# App UI
st.title("Teacher Scheduling Assistant")
st.markdown("""
This tool helps teachers create and manage schedules, including:
- Weekly timetables
- Annual lesson plans
- Monthly lesson plans
- Weekly lesson plans
""")

# Sidebar for navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select Mode", ["Create Schedule", "Refine Schedule", "View History"])

if app_mode == "Create Schedule":
    st.header("Create New Schedule")
    
    # Schedule type selection
    schedule_type = st.selectbox(
        "Select Schedule Type",
        ["Weekly Timetable", "Annual Lesson Plan", "Monthly Lesson Plan", "Weekly Lesson Plan"],
        index=0
    )
    
    # Input method selection
    input_method = st.radio(
        "Input Method",
        ["Text Input", "Voice Input", "Document Upload"],
        horizontal=True
    )
    
    # Language selection
    language = st.selectbox(
        "Language",
        ["English", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati"],
        index=0
    )
    
    # Preferences
    with st.expander("Additional Preferences (Optional)"):
        st.write("Specify any preferences for your schedule")
        preferences = {}
        
        if "Timetable" in schedule_type:
            preferences["working_days"] = st.multiselect(
                "Working Days",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            )
            preferences["periods_per_day"] = st.slider("Number of periods per day", 4, 10, 6)
            preferences["break_after"] = st.slider("Break after how many periods?", 2, 5, 3)
        else:
            preferences["teaching_methods"] = st.multiselect(
                "Preferred Teaching Methods",
                ["Lecture", "Discussion", "Group Work", "Project-Based", "Demonstration", "Other"]
            )
            preferences["assessment_types"] = st.multiselect(
                "Preferred Assessment Types",
                ["Quizzes", "Tests", "Projects", "Presentations", "Class Participation"]
            )
    
    # Input section based on method
    input_content = ""
    document_type = None
    
    if input_method == "Text Input":
        input_content = st.text_area("Enter your schedule requirements", height=150)
    elif input_method == "Voice Input":
        audio_file = st.file_uploader("Upload Audio File", type=["wav", "mp3"])
        if audio_file:
            st.audio(audio_file)
    elif input_method == "Document Upload":
        document_type = st.radio(
            "Document Type",
            ["Excel", "PDF"],
            horizontal=True
        )
        document_file = st.file_uploader(f"Upload {document_type} File", type=["xlsx", "pdf"])
    
    # Generate button
    if st.button("Generate Schedule"):
        if (input_method == "Text Input" and not input_content) or \
           (input_method == "Voice Input" and not audio_file) or \
           (input_method == "Document Upload" and not document_file):
            st.error("Please provide input based on your selected method")
        else:
            with st.spinner("Generating schedule..."):
                try:
                    # Prepare request data
                    files = {}
                    data = {
                        "schedule_type": schedule_type.lower().replace(" ", "_"),
                        "input_method": input_method.lower().replace(" ", "_"),
                        "language": language.lower(),
                        "preferences": json.dumps(preferences) if preferences else None
                    }
                    
                    if input_method == "Text Input":
                        data["text_input"] = input_content
                    elif input_method == "Voice Input":
                        files["audio_file"] = audio_file.getvalue()
                    elif input_method == "Document Upload":
                        files["document_file"] = document_file.getvalue()
                        data["document_type"] = document_type.lower()
                    
                    # Call FastAPI backend
                    response = requests.post(
                        f"{BACKEND_URL}/generate_schedule",
                        data=data,
                        files=files
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result["status"] == "success":
                            st.session_state.current_schedule = result["schedule"]
                            st.session_state.schedule_history.append(result["schedule"])
                            st.success("Schedule generated successfully!")
                            
                            # Display the schedule
                            display_schedule(result["schedule"])
                            try:
                                if isinstance(result["schedule"], dict):
                                    if "schedule" in result["schedule"]:  # Timetable format
                                        df = pd.DataFrame(result["schedule"]["schedule"])
                                        st.write("### Weekly Timetable")
                                        st.table(df)
                                        
                                        if "breaks" in result["schedule"]:
                                            st.write("**Break Times:**")
                                            st.json(result["schedule"]["breaks"])
                                    else:  # Lesson plan format
                                        st.json(result["schedule"])
                                else:
                                    st.write(result["schedule"])
                            except Exception as e:
                                st.error(f"Display error: {str(e)}")
                                st.json(result["schedule"])
                            
                            # Download options...
                            col1, col2 = st.columns(2)
                            with col1:
                                json_data, json_ext = save_to_file(result["schedule"], 'json')
                                st.download_button(
                                    label="Download as JSON",
                                    data=json_data,
                                    file_name=f"schedule.{json_ext}",
                                    mime="application/json"
                                )
                            with col2:
                                excel_data, excel_ext = save_to_file(result["schedule"], 'excel')
                                st.download_button(
                                    label="Download as Excel",
                                    data=excel_data,
                                    file_name=f"schedule.{excel_ext}",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        else:
                            st.error(f"Error: {result.get('message', 'Unknown error')}")
                            if "raw_response" in result:
                                st.text_area("Raw AI Response", value=result["raw_response"], height=200)
                        
                    else:
                        st.error(f"API Error: {response.text}")
                except Exception as e:
                    st.error(f"Error generating schedule: {str(e)}")

elif app_mode == "Refine Schedule" and st.session_state.current_schedule:
    st.header("Refine Current Schedule")
    st.subheader("Current Schedule")
    display_schedule(st.session_state.current_schedule)
    
    feedback = st.text_area("What changes would you like to make?", height=100)
    
    if st.button("Apply Changes"):
        if not feedback:
            st.warning("Please provide feedback for refinement")
        else:
            with st.spinner("Refining schedule..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/refine_schedule",
                        data={
                            "current_schedule": json.dumps(st.session_state.current_schedule),
                            "feedback": feedback
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result["status"] == "success":
                            st.session_state.current_schedule = result["schedule"]
                            st.session_state.schedule_history.append(result["schedule"])
                            st.success("Schedule refined successfully!")
                            display_schedule(result["schedule"])
                        else:
                            st.error(f"Error: {result.get('message', 'Unknown error')}")
                    else:
                        st.error(f"API Error: {response.text}")
                except Exception as e:
                    st.error(f"Error refining schedule: {str(e)}")

elif app_mode == "View History":
    st.header("Schedule History")
    if not st.session_state.schedule_history:
        st.info("No schedule history available")
    else:
        selected_index = st.selectbox(
            "Select a schedule to view",
            range(len(st.session_state.schedule_history)),
            format_func=lambda x: f"Schedule {x+1}"
        )
        display_schedule(st.session_state.schedule_history[selected_index])

else:
    st.info("Please create a schedule first")

# Footer
st.markdown("---")
st.markdown("Government of India - Teacher Support Tool")
