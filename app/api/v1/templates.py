from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.templates import TemplateUploadResponse, TemplatePreviewResponse
from app.services.template_service import template_service
from app.core.logging import logger

router = APIRouter(prefix="/templates", tags=["Templates"])

@router.post("/upload", response_model=TemplateUploadResponse)
async def upload_template(file: UploadFile = File(...)):
    content = await file.read()
    result = await template_service.save_template(file.filename, content)
    return result

@router.get("/{template_id}/preview", response_model=TemplatePreviewResponse)
async def preview_template(template_id: str):
    result = await template_service.get_template_preview(template_id)
    return result

@router.get("/", summary="Listar plantillas")
async def list_templates():
    return await template_service.list_templates()

@router.delete("/{template_id}", summary="Eliminar plantilla")
async def delete_template(template_id: str):
    await template_service.delete_template(template_id)
    return {"message": f"Plantilla {template_id} eliminada correctamente"}