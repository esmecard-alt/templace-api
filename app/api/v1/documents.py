import base64
from fastapi import APIRouter
from fastapi.responses import Response
from app.models.documents import GenerateRequest, GenerateResponse, OutputFormat
from app.services.document_service import document_service
from app.core.logging import logger

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/generate")
async def generate_document(request: GenerateRequest):
    result = await document_service.generate(
        template_id=request.template_id,
        data=request.data,
        output_format=request.output_format,
        filename=request.filename,
        strict_mode=request.strict_mode
    )

    if request.output_format == OutputFormat.base64:
        return result

    content = base64.b64decode(result["base64_content"])
    media_type = "application/pdf" if request.output_format == OutputFormat.pdf \
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={result['filename']}"
        }
    )