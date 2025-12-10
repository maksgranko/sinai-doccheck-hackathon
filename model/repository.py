"""
Репозиторий: обращается к внешнему PHP API, без прямого доступа к БД.
"""
import time
from typing import Optional
from kivy.logger import Logger

from model.document_model import DocumentModel
from services.api_client import ApiClient
import config


class ApiRepository:
    """Работа с внешним API"""
    
    def __init__(self):
        self.client = ApiClient()
        self.max_retries = config.MAX_RETRIES
        Logger.info(f"Repository: Работаем через внешний API {config.API_BASE_URL}")
        
    def verify_document(
        self, 
        document_id: str, 
        pin_code: Optional[str] = None,
        max_retries: Optional[int] = None
    ) -> Optional[DocumentModel]:
        """
        Верификация документа через внешний API.
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        for attempt in range(max_retries):
            try:
                return self.client.verify_document(document_id, pin_code)
            except Exception as e:
                Logger.error(f"Repository: Ошибка запроса к API: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    Logger.info(f"Repository: Ожидание {wait_time} секунд перед повтором")
                    time.sleep(wait_time)
                    continue
                return DocumentModel(
                    document_id=document_id,
                    status='invalid',
                    metadata={'error': str(e)}
                )
    
    def get_document_types(self) -> list:
        """
        Типы документов недоступны без БД; возвращаем пусто.
        """
        return []
    
    def get_verification_templates(self) -> list:
        """
        Получение шаблонов проверки (заглушка, можно расширить)
        
        Returns:
            Список шаблонов
        """
        # Можно добавить таблицу templates в БД
        return [
            {
                "id": "template1",
                "name": "Стандартная проверка",
                "checks": ["validity", "issuer", "signature", "expiry"]
            },
            {
                "id": "template2",
                "name": "Расширенная проверка",
                "checks": ["validity", "issuer", "signature", "expiry", "revocation", "chain"]
            }
        ]
