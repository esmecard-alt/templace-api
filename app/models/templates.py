from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TemplateUploadResponse(BaseModel):
    template_id: str
    filename: str
    size_kb: float
    markers_detected: list[str]
    uploaded_at: datetime

class TemplatePreviewResponse(BaseModel):
    template_id: str
    filename: str
    markers: list[str]
    size_kb: float