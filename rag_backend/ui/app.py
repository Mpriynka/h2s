# ui/app.py
import streamlit as st
import requests
import os

st.title("PDF to Knowledge Base Uploader")

# Configuration
BACKEND_URL = "http://localhost:8000"  # Change if your backend is elsewhere

# File upload section
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save the file temporarily
    temp_file = f"temp_{uploaded_file.name}"
    with open(temp_file, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Send to backend
    if st.button("Upload to Knowledge Base"):
        try:
            files = {"file": open(temp_file, "rb")}
            response = requests.post(f"{BACKEND_URL}/upload/", files=files)
            
            if response.status_code == 200:
                result = response.json()
                st.success("PDF processed successfully!")
                st.json(result)
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            # Clean up
            files["file"].close()
            os.remove(temp_file)

# Status check
if st.button("Check Knowledge Base Status"):
    try:
        response = requests.get(f"{BACKEND_URL}/health/")
        if response.status_code == 200:
            st.success("Knowledge Base is healthy!")
            # Check if vector store exists
            if os.path.exists("faiss_index"):
                st.info("Vector store contains documents")
            else:
                st.info("Vector store is empty")
        else:
            st.error(f"Error: {response.text}")
    except Exception as e:
        st.error(f"Could not connect to backend: {str(e)}")