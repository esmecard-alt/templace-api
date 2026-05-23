from pydantic import BaseModel
from typing import Any, Optional
from enum import Enum

class OutputFormat(str, Enum):
    docx = "docx"
    pdf = "pdf"
    base64 = "base64"

class GenerateRequest(BaseModel):
    template_id: str
    data: dict[str, Any]
    output_format: OutputFormat = OutputFormat.docx
    filename: Optional[str] = None

class GenerateResponse(BaseModel):
    filename: str
    output_format: str
    size_kb: float
    download_url: Optional[str] = None
    base64_content: Optional[str] = None