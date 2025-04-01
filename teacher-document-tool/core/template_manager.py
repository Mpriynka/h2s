# core/template_manager.py
import os
import json

def create_default_templates():
    """Create default templates if none exist"""
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Official Letter Template
    official_letter = {
        "id": "official_letter",
        "name": "Official Letter",
        "description": "Formal letter for official communication with authorities",
        "prompt_template": """
        Write a formal letter with the following details:
        - From: {sender_name}, {sender_designation}, {sender_school}
        - To: {recipient_name}, {recipient_designation}, {recipient_organization}
        - Subject: {subject}
        - Date: {date}
        
        The letter should be about: {letter_content}
        
        The tone should be: {formality}
        The language should be: {language}
        
        Include all formal letter components (letterhead, subject, salutation, body, closing, signature).
        """,
        "required_fields": [
            {"name": "sender_name", "description": "Name of the sender"},
            {"name": "sender_designation", "description": "Designation of the sender"},
            {"name": "sender_school", "description": "School name of the sender"},
            {"name": "recipient_name", "description": "Name of the recipient"},
            {"name": "recipient_designation", "description": "Designation of the recipient"},
            {"name": "recipient_organization", "description": "Organization of the recipient"},
            {"name": "subject", "description": "Subject of the letter"},
            {"name": "date", "description": "Date of the letter"},
            {"name": "letter_content", "description": "Main points to include in the letter"}
        ]
    }
    
    # Email Template
    email_template = {
        "id": "email",
        "name": "Professional Email",
        "description": "Professional email for communication with parents, colleagues or authorities",
        "prompt_template": """
        Write a professional email with the following details:
        - From: {sender_name}, {sender_designation}, {sender_school}
        - To: {recipient_name}
        - Subject: {subject}
        
        The email should be about: {email_content}
        
        The tone should be: {formality}
        The language should be: {language}
        
        Include all professional email components (subject line, greeting, body, closing, signature).
        """,
        "required_fields": [
            {"name": "sender_name", "description": "Name of the sender"},
            {"name": "sender_designation", "description": "Designation of the sender"},
            {"name": "sender_school", "description": "School name of the sender"},
            {"name": "recipient_name", "description": "Name of the recipient(s)"},
            {"name": "subject", "description": "Subject of the email"},
            {"name": "email_content", "description": "Main points to include in the email"}
        ]
    }
    
    # Circular Template
    circular = {
        "id": "circular",
        "name": "School Circular",
        "description": "Announcements and notifications for school community",
        "prompt_template": """
        Create a school circular with the following details:
        - School Name: {school_name}
        - Circular Number: {circular_number}
        - Date: {date}
        - Subject: {subject}
        
        The circular should announce: {announcement}
        
        Additional details to include: {additional_details}
        
        The tone should be: {formality}
        The language should be: {language}
        
        Format it as a proper school circular with header, reference number, body, and signature from {authority_name}, {authority_designation}.
        """,
        "required_fields": [
            {"name": "school_name", "description": "Name of the school"},
            {"name": "circular_number", "description": "Reference number of the circular"},
            {"name": "date", "description": "Date of issue"},
            {"name": "subject", "description": "Subject of the circular"},
            {"name": "announcement", "description": "Main announcement content"},
            {"name": "additional_details", "description": "Any additional information"},
            {"name": "authority_name", "description": "Name of the issuing authority"},
            {"name": "authority_designation", "description": "Designation of the issuing authority"}
        ]
    }
    
    # Save default templates
    for template in [official_letter, email_template, circular]:
        template_path = os.path.join(templates_dir, f"{template['id']}.json")
        if not os.path.exists(template_path):
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=4)

def get_all_templates():
    """Get all available templates"""
    # Create default templates if none exist
    create_default_templates()
    
    templates_dir = "templates"
    templates = {}
    
    for filename in os.listdir(templates_dir):
        if filename.endswith(".json"):
            with open(os.path.join(templates_dir, filename), 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                templates[template_data["id"]] = template_data
    
    return templates

def load_template_by_id(template_id):
    """Load template by id"""
    templates = get_all_templates()
    return templates.get(template_id)