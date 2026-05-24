from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import TemplaceException, templace_exception_handler
from app.api.v1.templates import router as templates_router
from app.api.v1.documents import router as documents_router
from app.api.v1.excel import router as excel_router

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="REST API for generating documents from .docx templates",
    version=settings.VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(TemplaceException, templace_exception_handler)

app.include_router(templates_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(excel_router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    logger.info(f"Templace API arrancando — entorno: {settings.ENV}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}