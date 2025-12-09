"""
Модель документа в БД
"""
from sqlalchemy import Column, Integer, String, Date, JSON, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base


class Document(Base):
    """Модель документа"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), unique=True, nullable=False, index=True)
    document_type = Column(String(100))
    issuer = Column(String(255))
    issue_date = Column(Date)
    expiry_date = Column(Date, index=True)
    status = Column(String(20), nullable=False, index=True)  # valid, warning, invalid, revoked
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_document_id', 'document_id'),
        Index('idx_status', 'status'),
        Index('idx_expiry_date', 'expiry_date'),
    )


