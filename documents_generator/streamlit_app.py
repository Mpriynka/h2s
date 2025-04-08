# streamlit_app.py
import streamlit as st
import requests
import json
import os

# Define API endpoint (adjust if needed)
API_BASE_URL = "http://localhost:8001/api/documents"

def main():
    st.title("Document Generator for Government of India Teachers")
    st.write("Generate professional documents with minimal input")

    # Fetch available templates
    templates = fetch_templates()

    if not templates:
        st.error("Failed to load templates. Make sure the API server is running.")
        return

    # Document type selection
    template_options = {template["name"]: template["id"] for template in templates}
    template_name = st.selectbox("Select Document Type", options=list(template_options.keys()))
    template_id = template_options[template_name]

    # Get the selected template details
    selected_template = next((t for t in templates if t["id"] == template_id), None)

    if selected_template:
        st.write(f"**Description:** {selected_template['description']}")

        # Language selection
        language = st.selectbox(
            "Language",
            ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam", "Marathi", "Bengali", "Gujarati", "Punjabi"]
        )

        # Formality selection
        formality = st.selectbox(
            "Tone & Formality",
            ["formal", "semi-formal", "casual"]
        )

        # Create form for template fields
        with st.form(key="document_form"):
            st.subheader("Document Details")

            # Generate form fields from template requirements
            field_values = {}
            for field in selected_template["required_fields"]:
                field_values[field["name"]] = st.text_input(field["description"], key=field["name"])

            submit_button = st.form_submit_button(label="Generate Document")

        if submit_button:
            # Check if all required fields are filled
            if all(field_values.values()):
                # Generate document
                with st.spinner("Generating document..."):
                    document = generate_document(template_id, language, formality, field_values)

                if document:
                    st.success("Document generated successfully!")
                    st.text_area("Generated Document", document["content"], height=400)

                    # Download button
                    document_text = document["content"]
                    st.download_button(
                        label="Download Document",
                        data=document_text,
                        file_name=f"{template_id}_{language.lower()}.txt",
                        mime="text/plain"
                    )
            else:
                st.warning("Please fill in all required fields.")

def fetch_templates():
    """Fetch templates from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/templates")
        response.raise_for_status()
        return response.json()
    except:
        return None

def generate_document(template_id, language, formality, details):
    """Generate a document using the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json={
                "template_type": template_id,
                "language": language,
                "formality": formality,
                "details": details
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error generating document: {str(e)}")
        return None

if __name__ == "__main__":
    main()