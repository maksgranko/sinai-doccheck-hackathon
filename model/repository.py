"""
Репозиторий для работы с API сервера
"""
import requests
import time
from typing import Optional, Dict, Any
from kivy.logger import Logger

from model.document_model import DocumentModel
import config


class ApiRepository:
    """Репозиторий для взаимодействия с сервером API"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Инициализация репозитория
        
        Args:
            base_url: Базовый URL API сервера (если None, используется из config)
        """
        self.base_url = base_url or config.API_BASE_URL
        self.session = requests.Session()
        self.session.verify = True  # Включение проверки SSL сертификата
        
    def verify_document(
        self, 
        document_id: str, 
        pin_code: Optional[str] = None,
        max_retries: int = 3
    ) -> Optional[DocumentModel]:
        """
        Верификация документа по ID с экспоненциальным откатом
        
        Args:
            document_id: ID документа из QR-кода
            pin_code: PIN-код для аутентификации (опционально)
            max_retries: Максимальное количество попыток
            
        Returns:
            DocumentModel или None в случае ошибки
        """
        endpoint = f"{self.base_url}/documents/verify"
        
        payload = {
            "document_id": document_id
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if pin_code:
            headers["X-PIN-Code"] = pin_code
        
        # Экспоненциальный откат
        for attempt in range(max_retries):
            try:
                Logger.info(f"Repository: Попытка {attempt + 1} верификации документа {document_id}")
                
                response = self.session.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    Logger.info(f"Repository: Документ успешно верифицирован")
                    return self._parse_response(data)
                
                elif response.status_code == 404:
                    Logger.warning(f"Repository: Документ не найден")
                    return DocumentModel(
                        document_id=document_id,
                        status='invalid',
                        metadata={'error': 'Документ не найден в реестре'}
                    )
                
                elif response.status_code == 401:
                    Logger.error(f"Repository: Ошибка аутентификации")
                    return DocumentModel(
                        document_id=document_id,
                        status='invalid',
                        metadata={'error': 'Ошибка аутентификации'}
                    )
                
                else:
                    Logger.warning(f"Repository: Неожиданный статус {response.status_code}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Экспоненциальный откат
                        Logger.info(f"Repository: Ожидание {wait_time} секунд перед повтором")
                        time.sleep(wait_time)
                        continue
                    else:
                        return DocumentModel(
                            document_id=document_id,
                            status='invalid',
                            metadata={'error': f'Ошибка сервера: {response.status_code}'}
                        )
            
            except requests.exceptions.Timeout:
                Logger.warning(f"Repository: Таймаут запроса (попытка {attempt + 1})")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    return DocumentModel(
                        document_id=document_id,
                        status='invalid',
                        metadata={'error': 'Таймаут соединения'}
                    )
            
            except requests.exceptions.ConnectionError as e:
                Logger.error(f"Repository: Ошибка соединения: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    return DocumentModel(
                        document_id=document_id,
                        status='invalid',
                        metadata={'error': 'Ошибка соединения с сервером'}
                    )
            
            except Exception as e:
                Logger.error(f"Repository: Неожиданная ошибка: {e}")
                return DocumentModel(
                    document_id=document_id,
                    status='invalid',
                    metadata={'error': str(e)}
                )
        
        return None
    
    def _parse_response(self, data: Dict[str, Any]) -> DocumentModel:
        """
        Парсинг ответа от сервера
        
        Args:
            data: JSON данные от сервера
            
        Returns:
            DocumentModel
        """
        status = data.get('status', 'invalid')
        
        # Определение статуса документа
        if status == 'valid':
            doc_status = 'valid'
        elif status == 'expiring_soon' or status == 'warning':
            doc_status = 'warning'
        else:
            doc_status = 'invalid'
        
        return DocumentModel(
            document_id=data.get('document_id', ''),
            status=doc_status,
            document_type=data.get('document_type'),
            issuer=data.get('issuer'),
            issue_date=data.get('issue_date'),
            expiry_date=data.get('expiry_date'),
            metadata=data.get('metadata', {})
        )
    
    def get_document_types(self) -> list:
        """
        Получение списка типов документов
        
        Returns:
            Список типов документов
        """
        endpoint = f"{self.base_url}/document-types"
        
        try:
            response = self.session.get(endpoint, timeout=5)
            if response.status_code == 200:
                return response.json().get('types', [])
        except Exception as e:
            Logger.error(f"Repository: Ошибка получения типов документов: {e}")
        
        return []
    
    def get_verification_templates(self) -> list:
        """
        Получение шаблонов проверки
        
        Returns:
            Список шаблонов
        """
        endpoint = f"{self.base_url}/verification-templates"
        
        try:
            response = self.session.get(endpoint, timeout=5)
            if response.status_code == 200:
                return response.json().get('templates', [])
        except Exception as e:
            Logger.error(f"Repository: Ошибка получения шаблонов: {e}")
        
        return []

