"""
API endpoints для работы с документами
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentVerifyRequest, DocumentResponse, DocumentErrorResponse
from app.services.verification_service import VerificationService

router = APIRouter()


@router.post("/verify", response_model=DocumentResponse)
@router.get("/verify", response_model=DocumentResponse)
async def verify_document(
    request: Optional[DocumentVerifyRequest] = None,
    document_id: Optional[str] = None,  # Для GET запросов
    pin_code: Optional[str] = Header(None, alias="X-PIN-Code"),
    db: Session = Depends(get_db)
):
    """
    Верификация документа по ID
    
    Поддерживает как POST (с JSON телом), так и GET (с query параметром document_id)
    
    - **document_id**: ID документа из QR-кода
    - **X-PIN-Code**: PIN-код для аутентификации (опционально)
    """
    # Определяем document_id из запроса
    doc_id = document_id or (request.document_id if request else None)
    
    if not doc_id:
        raise HTTPException(
            status_code=400,
            detail="document_id обязателен"
        )
    
    # Поиск документа в БД
    document = db.query(Document).filter(
        Document.document_id == doc_id
    ).first()
    
    if not document:
        # Документ не найден
        return DocumentErrorResponse(
            document_id=doc_id,
            error="Документ не найден в реестре"
        )
    
    # Проверка PIN (если требуется)
    if pin_code:
        # Здесь можно добавить проверку PIN
        # Для примера просто проверяем, что PIN не пустой
        if not pin_code or len(pin_code) < 4:
            raise HTTPException(
                status_code=401,
                detail="Неверный PIN-код"
            )
    
    # Определение статуса документа
    status = VerificationService.determine_status(document)
    
    return DocumentResponse(
        document_id=document.document_id,
        status=status,
        document_type=document.document_type,
        issuer=document.issuer,
        issue_date=document.issue_date,
        expiry_date=document.expiry_date,
        metadata=document.metadata or {}
    )



