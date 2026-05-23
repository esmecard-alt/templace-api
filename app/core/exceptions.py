from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.logging import logger

class TemplaceException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class TemplateNotFoundException(TemplaceException):
    def __init__(self, template_id: str):
        super().__init__(
            code="TEMPLATE_NOT_FOUND",
            message=f"No existe ninguna plantilla con id '{template_id}'",
            status_code=404
        )

class TemplateTooBigException(TemplaceException):
    def __init__(self, size_mb: float, max_mb: int):
        super().__init__(
            code="TEMPLATE_TOO_BIG",
            message=f"La plantilla ocupa {size_mb:.1f}MB, el máximo permitido es {max_mb}MB",
            status_code=400
        )

class InvalidTemplateException(TemplaceException):
    def __init__(self, detail: str):
        super().__init__(
            code="INVALID_TEMPLATE",
            message=f"El archivo no es una plantilla válida: {detail}",
            status_code=400
        )

class GenerationException(TemplaceException):
    def __init__(self, detail: str):
        super().__init__(
            code="GENERATION_FAILED",
            message=f"Error al generar el documento: {detail}",
            status_code=500
        )

async def templace_exception_handler(request: Request, exc: TemplaceException):
    logger.error(f"[{exc.code}] {exc.message} — {request.method} {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )