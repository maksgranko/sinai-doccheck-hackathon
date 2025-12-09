"""
ViewModel для экрана истории верификаций
"""
from typing import List
from kivy.logger import Logger

from model.document_model import VerificationRecord
from model.storage import Storage


class HistoryViewModel:
    """ViewModel для работы с историей верификаций"""
    
    def __init__(self):
        """Инициализация ViewModel"""
        self.storage = Storage()
    
    def get_all_verifications(self, limit: int = 100) -> List[VerificationRecord]:
        """
        Получение всех записей верификации
        
        Args:
            limit: Максимальное количество записей
            
        Returns:
            Список записей
        """
        return self.storage.get_all_verifications(limit)
    
    def delete_verification(self, record_id: int) -> bool:
        """
        Удаление записи о верификации
        
        Args:
            record_id: ID записи
            
        Returns:
            True если успешно
        """
        return self.storage.delete_verification(record_id)
    
    def clear_all(self) -> bool:
        """
        Очистка всех записей
        
        Returns:
            True если успешно
        """
        return self.storage.clear_all()
    
    def get_status_color(self, status: str) -> tuple:
        """
        Получение цвета статуса
        
        Args:
            status: Статус документа
            
        Returns:
            Кортеж (R, G, B)
        """
        status_colors = {
            'valid': (0.2, 0.8, 0.2),      # Зеленый
            'warning': (1.0, 0.8, 0.0),    # Желтый
            'invalid': (0.9, 0.2, 0.2),    # Красный
        }
        return status_colors.get(status, (0.5, 0.5, 0.5))
    
    def get_status_text(self, status: str) -> str:
        """
        Получение текстового описания статуса
        
        Args:
            status: Статус документа
            
        Returns:
            Текстовое описание
        """
        status_texts = {
            'valid': 'Подлинный',
            'warning': 'Предупреждение',
            'invalid': 'Недействителен',
        }
        return status_texts.get(status, 'Неизвестно')



