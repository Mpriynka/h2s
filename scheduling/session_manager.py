import streamlit as st

def init_session_state():
    """Initialize all session state variables with default values"""
    defaults = {
        'current_schedule': None,
        'schedule_history': [],
        'multi_input': {
            'document': None,
            'text': "",
            'voice': ""
        },
        'recording': False,
        'schedule_type': "weekly_timetable",
        'preferences': {},
        'initialized': True  # Flag to indicate initialization is complete
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def safe_get(key, default=None):
    """Safely get a session state value with optional default"""
    init_session_state()  # Ensure initialization
    return st.session_state.get(key, default)