from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import TemplaceException, templace_exception_handler

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

@app.on_event("startup")
async def startup():
    logger.info(f"Templace API arrancando — entorno: {settings.ENV}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}