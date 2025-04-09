# app/models.py
from pydantic import BaseModel
from typing import Optional

class Query(BaseModel):
    text: str
    top_k: Optional[int] = 3