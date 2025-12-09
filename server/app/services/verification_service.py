"""
Сервис верификации документов
"""
from datetime import date, timedelta
from app.models.document import Document


class VerificationService:
    """Сервис для определения статуса документов"""
    
    @staticmethod
    def determine_status(document: Document) -> str:
        """
        Определение статуса документа
        
        Returns:
            'valid' - документ подлинный и действителен
            'warning' - документ подлинный, но есть предупреждение
            'invalid' - документ недействителен
        """
        # Если статус в БД - revoked или invalid
        if document.status in ['revoked', 'invalid']:
            return 'invalid'
        
        # Если статус в БД - valid, проверяем срок действия
        if document.status == 'valid':
            if document.expiry_date:
                days_until_expiry = (document.expiry_date - date.today()).days
                
                # Если срок истек
                if days_until_expiry < 0:
                    return 'invalid'
                
                # Если срок истекает в течение 30 дней
                if days_until_expiry <= 30:
                    return 'warning'
            
            return 'valid'
        
        # Если статус - warning
        if document.status == 'warning':
            return 'warning'
        
        # По умолчанию - invalid
        return 'invalid'
    
    @staticmethod
    def check_expiry_soon(expiry_date: date, days_threshold: int = 30) -> bool:
        """Проверка, истекает ли срок действия скоро"""
        if not expiry_date:
            return False
        
        days_until_expiry = (expiry_date - date.today()).days
        return 0 < days_until_expiry <= days_threshold


