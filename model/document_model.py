"""
Модель данных документа
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DocumentModel:
    """Модель электронного документа"""
    document_id: str
    status: str  # 'valid', 'warning', 'invalid'
    document_type: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    metadata: Optional[dict] = None
    
    def __post_init__(self):
        """Валидация данных после инициализации"""
        if self.status not in ['valid', 'warning', 'invalid']:
            raise ValueError(f"Неверный статус документа: {self.status}")


@dataclass
class VerificationRecord:
    """Запись о верификации документа"""
    id: Optional[int] = None
    document_id: str = ""
    status: str = ""
    timestamp: Optional[datetime] = None
    document_type: Optional[str] = None
    issuer: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для сохранения"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'document_type': self.document_type,
            'issuer': self.issuer
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VerificationRecord':
        """Создание из словаря"""
        timestamp = None
        if data.get('timestamp'):
            timestamp = datetime.fromisoformat(data['timestamp'])
        
        return cls(
            id=data.get('id'),
            document_id=data.get('document_id', ''),
            status=data.get('status', ''),
            timestamp=timestamp,
            document_type=data.get('document_type'),
            issuer=data.get('issuer')
        )




