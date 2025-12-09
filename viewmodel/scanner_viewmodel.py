"""
ViewModel для экрана сканирования
"""
from kivy.clock import Clock
from kivy.logger import Logger
from typing import Optional, Callable

from model.document_model import DocumentModel, VerificationRecord
from model.repository import ApiRepository
from model.storage import Storage


class ScannerViewModel:
    """ViewModel для обработки логики сканирования"""
    
    def __init__(self):
        """Инициализация ViewModel"""
        self.repository = ApiRepository()
        self.storage = Storage()
        self.current_document: Optional[DocumentModel] = None
        self.on_status_changed: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
    
    def verify_document(self, document_id: str, pin_code: Optional[str] = None):
        """
        Верификация документа по ID
        
        Args:
            document_id: ID документа из QR-кода
            pin_code: PIN-код для аутентификации
        """
        Logger.info(f"ViewModel: Начало верификации документа {document_id}")
        
        # Запуск верификации в отдельном потоке (симуляция через Clock)
        Clock.schedule_once(
            lambda dt: self._perform_verification(document_id, pin_code),
            0.1
        )
    
    def _perform_verification(self, document_id: str, pin_code: Optional[str]):
        """Выполнение верификации документа"""
        try:
            # Запрос к серверу
            document = self.repository.verify_document(document_id, pin_code)
            
            if document:
                self.current_document = document
                
                # Сохранение в журнал
                record = VerificationRecord(
                    document_id=document.document_id,
                    status=document.status,
                    document_type=document.document_type,
                    issuer=document.issuer
                )
                self.storage.save_verification(record)
                
                # Уведомление View об изменении статуса
                if self.on_status_changed:
                    self.on_status_changed(document)
                
                Logger.info(f"ViewModel: Верификация завершена, статус: {document.status}")
            else:
                error_msg = "Не удалось получить ответ от сервера"
                if self.on_error:
                    self.on_error(error_msg)
                Logger.error(f"ViewModel: {error_msg}")
        
        except Exception as e:
            error_msg = f"Ошибка верификации: {str(e)}"
            if self.on_error:
                self.on_error(error_msg)
            Logger.error(f"ViewModel: {error_msg}")
    
    def get_status_color(self, status: str) -> tuple:
        """
        Получение цвета статуса (RGB)
        
        Args:
            status: Статус документа
            
        Returns:
            Кортеж (R, G, B) в диапазоне 0-1
        """
        status_colors = {
            'valid': (0.2, 0.8, 0.2),      # Зеленый
            'warning': (1.0, 0.8, 0.0),    # Желтый
            'invalid': (0.9, 0.2, 0.2),    # Красный
        }
        return status_colors.get(status, (0.5, 0.5, 0.5))  # Серый по умолчанию
    
    def get_status_text(self, status: str) -> str:
        """
        Получение текстового описания статуса
        
        Args:
            status: Статус документа
            
        Returns:
            Текстовое описание
        """
        status_texts = {
            'valid': 'Документ подлинный',
            'warning': 'Предупреждение',
            'invalid': 'Документ недействителен',
        }
        return status_texts.get(status, 'Неизвестный статус')



