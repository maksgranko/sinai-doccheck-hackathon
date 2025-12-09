"""
Схемы для валидации данных документов
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date


class DocumentVerifyRequest(BaseModel):
    """Запрос на верификацию документа"""
    document_id: str = Field(..., description="ID документа из QR-кода")


class DocumentResponse(BaseModel):
    """Ответ с информацией о документе"""
    document_id: str
    status: str = Field(..., description="Статус: valid, warning, invalid")
    document_type: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class DocumentErrorResponse(BaseModel):
    """Ответ об ошибке"""
    document_id: str
    status: str = "invalid"
    error: str


