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
async def verify_document(
    request: DocumentVerifyRequest,
    pin_code: Optional[str] = Header(None, alias="X-PIN-Code"),
    db: Session = Depends(get_db)
):
    """
    Верификация документа по ID
    
    - **document_id**: ID документа из QR-кода
    - **X-PIN-Code**: PIN-код для аутентификации (опционально)
    """
    # Поиск документа в БД
    document = db.query(Document).filter(
        Document.document_id == request.document_id
    ).first()
    
    if not document:
        # Документ не найден
        return DocumentErrorResponse(
            document_id=request.document_id,
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


