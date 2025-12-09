"""
Локальное хранилище для журнала верификаций
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from kivy.logger import Logger

from model.document_model import VerificationRecord


class Storage:
    """Класс для работы с локальной базой данных"""
    
    def __init__(self, db_path: str = "verification_history.db"):
        """
        Инициализация хранилища
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Инициализация таблиц базы данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    document_type TEXT,
                    issuer TEXT,
                    metadata TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            Logger.info("Storage: База данных инициализирована")
        except Exception as e:
            Logger.error(f"Storage: Ошибка инициализации БД: {e}")
    
    def save_verification(self, record: VerificationRecord) -> int:
        """
        Сохранение записи о верификации
        
        Args:
            record: Запись о верификации
            
        Returns:
            ID сохраненной записи
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = record.timestamp or datetime.now()
            metadata_json = json.dumps(record.to_dict())
            
            cursor.execute('''
                INSERT INTO verifications 
                (document_id, status, timestamp, document_type, issuer, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                record.document_id,
                record.status,
                timestamp.isoformat(),
                record.document_type,
                record.issuer,
                metadata_json
            ))
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            Logger.info(f"Storage: Запись сохранена с ID {record_id}")
            return record_id
        except Exception as e:
            Logger.error(f"Storage: Ошибка сохранения записи: {e}")
            return -1
    
    def get_all_verifications(self, limit: Optional[int] = None) -> List[VerificationRecord]:
        """
        Получение всех записей верификации
        
        Args:
            limit: Максимальное количество записей
            
        Returns:
            Список записей
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT * FROM verifications ORDER BY timestamp DESC'
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            records = []
            for row in rows:
                record = VerificationRecord(
                    id=row[0],
                    document_id=row[1],
                    status=row[2],
                    timestamp=datetime.fromisoformat(row[3]),
                    document_type=row[4],
                    issuer=row[5]
                )
                records.append(record)
            
            Logger.info(f"Storage: Получено {len(records)} записей")
            return records
        except Exception as e:
            Logger.error(f"Storage: Ошибка получения записей: {e}")
            return []
    
    def delete_verification(self, record_id: int) -> bool:
        """
        Удаление записи о верификации
        
        Args:
            record_id: ID записи
            
        Returns:
            True если успешно
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM verifications WHERE id = ?', (record_id,))
            conn.commit()
            conn.close()
            
            Logger.info(f"Storage: Запись {record_id} удалена")
            return True
        except Exception as e:
            Logger.error(f"Storage: Ошибка удаления записи: {e}")
            return False
    
    def clear_all(self) -> bool:
        """
        Очистка всех записей
        
        Returns:
            True если успешно
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM verifications')
            conn.commit()
            conn.close()
            
            Logger.info("Storage: Все записи удалены")
            return True
        except Exception as e:
            Logger.error(f"Storage: Ошибка очистки БД: {e}")
            return False



