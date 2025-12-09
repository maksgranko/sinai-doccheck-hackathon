"""
Главный файл FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.database import engine, Base
from app.api import documents, types

# Создание таблиц БД
Base.metadata.create_all(bind=engine)

# Создание приложения
app = FastAPI(
    title="Document Verifier API",
    description="API для верификации электронных документов",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(documents.router, prefix="/v1/documents", tags=["documents"])
app.include_router(types.router, prefix="/v1", tags=["types"])


@app.get("/health")
async def health_check():
    """Проверка здоровья сервера"""
    return {"status": "ok", "service": "document-verifier-api"}


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Document Verifier API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG
    )


