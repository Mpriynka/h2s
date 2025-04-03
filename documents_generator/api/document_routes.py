# api/document_routes.py
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import os
from core.document_generator import generate_document_content
from core.template_manager import get_all_templates, load_template_by_id

router = APIRouter()

# Models for request/response
class DocumentRequest(BaseModel):
    template_type: str  # e.g., "official_letter", "email", "circular"
    language: str = "English"  # Default language
    formality: str = "formal"  # "formal", "semi-formal", "casual"
    details: Dict[str, Any]  # Template-specific details

class DocumentResponse(BaseModel):
    content: str
    template_used: str
    language: str
    formality: str
    metadata: Dict[str, Any] = {}

class TemplateInfo(BaseModel):
    id: str
    name: str
    description: str
    required_fields: List[Dict[str, str]]

@router.get("/templates", response_model=List[TemplateInfo])
async def get_templates():
    """Get all available document templates"""
    templates = get_all_templates()
    template_list = []

    for template_id, template_data in templates.items():
        template_list.append(TemplateInfo(
            id=template_id,
            name=template_data["name"],
            description=template_data["description"],
            required_fields=template_data["required_fields"]
        ))

    return template_list

@router.post("/generate", response_model=DocumentResponse)
async def generate_document(request: DocumentRequest):
    """Generate a document based on template and provided details"""
    # Load the template
    template = load_template_by_id(request.template_type)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{request.template_type}' not found")

    # Validate required fields
    for field in template["required_fields"]:
        field_name = field["name"]
        if field_name not in request.details:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required field: {field_name} - {field.get('description', '')}"
            )

    # Generate the document content
    content = generate_document_content(
        template=template,
        language=request.language,
        formality=request.formality,
        details=request.details
    )

    # Build response
    response = DocumentResponse(
        content=content,
        template_used=request.template_type,
        language=request.language,
        formality=request.formality,
        metadata={
            "template_name": template["name"],
            "user_inputs": request.details
        }
    )

    return response

@router.post("/upload-template")
async def upload_template(template_file: UploadFile = File(...)):
    """Upload a new document template"""
    try:
        # Create templates directory if it doesn't exist
        templates_dir = "templates"
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)

        content = await template_file.read()
        template_data = json.loads(content)

        # Validate template structure
        required_keys = ["id", "name", "description", "prompt_template", "required_fields"]
        for key in required_keys:
            if key not in template_data:
                raise HTTPException(status_code=400, detail=f"Template missing required key: {key}")

        # Save template
        with open(os.path.join(templates_dir, f"{template_data['id']}.json"), 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=4)

        return {"message": f"Template '{template_data['name']}' uploaded successfully"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))