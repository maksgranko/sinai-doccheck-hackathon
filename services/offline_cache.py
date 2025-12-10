"""
Сервис офлайн кэширования и синхронизации
KILLER FEATURE #2: Офлайн режим с синхронизацией
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from kivy.logger import Logger

from model.document_model import DocumentModel, VerificationRecord


class OfflineCache:
    """Кэш для офлайн работы"""
    
    def __init__(self, cache_db_path="offline_cache.db"):
        """
        Инициализация кэша
        
        Args:
            cache_db_path: Путь к базе данных кэша
        """
        self.cache_db_path = Path(cache_db_path)
        self._init_cache_db()
    
    def _init_cache_db(self):
        """Инициализация базы данных кэша"""
        try:
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()
            
            # Таблица для кэшированных документов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cached_documents (
                    document_id TEXT PRIMARY KEY,
                    document_data TEXT NOT NULL,
                    cached_at TEXT NOT NULL,
                    synced INTEGER DEFAULT 0
                )
            ''')
            
            # Таблица для отложенных верификаций
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pending_verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    pin_code TEXT,
                    created_at TEXT NOT NULL,
                    synced INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            Logger.info("OfflineCache: База данных кэша инициализирована")
        except Exception as e:
            Logger.error(f"OfflineCache: Ошибка инициализации БД: {e}")
    
    def cache_document(self, document: DocumentModel):
        """
        Кэширование документа для офлайн доступа
        
        Args:
            document: DocumentModel объект
        """
        try:
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()
            
            document_data = json.dumps({
                'document_id': document.document_id,
                'status': document.status,
                'document_type': document.document_type,
                'issuer': document.issuer,
                'issue_date': str(document.issue_date) if document.issue_date else None,
                'expiry_date': str(document.expiry_date) if document.expiry_date else None,
                'metadata': document.metadata
            })
            
            cursor.execute('''
                INSERT OR REPLACE INTO cached_documents 
                (document_id, document_data, cached_at, synced)
                VALUES (?, ?, ?, 1)
            ''', (
                document.document_id,
                document_data,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            Logger.info(f"OfflineCache: Документ {document.document_id} закэширован")
        except Exception as e:
            Logger.error(f"OfflineCache: Ошибка кэширования документа: {e}")
    
    def get_cached_document(self, document_id: str) -> Optional[DocumentModel]:
        """
        Получение документа из кэша
        
        Args:
            document_id: ID документа
            
        Returns:
            DocumentModel или None
        """
        try:
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT document_data FROM cached_documents
                WHERE document_id = ?
            ''', (document_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                data = json.loads(row[0])
                return DocumentModel(
                    document_id=data['document_id'],
                    status=data['status'],
                    document_type=data.get('document_type'),
                    issuer=data.get('issuer'),
                    issue_date=data.get('issue_date'),
                    expiry_date=data.get('expiry_date'),
                    metadata=data.get('metadata')
                )
            return None
        except Exception as e:
            Logger.error(f"OfflineCache: Ошибка получения документа из кэша: {e}")
            return None
    
    def add_pending_verification(self, document_id: str, pin_code: Optional[str] = None):
        """
        Добавление отложенной верификации
        
        Args:
            document_id: ID документа
            pin_code: PIN-код (опционально)
        """
        try:
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO pending_verifications 
                (document_id, pin_code, created_at, synced)
                VALUES (?, ?, ?, 0)
            ''', (
                document_id,
                pin_code,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            Logger.info(f"OfflineCache: Добавлена отложенная верификация для {document_id}")
        except Exception as e:
            Logger.error(f"OfflineCache: Ошибка добавления отложенной верификации: {e}")
    
    def get_pending_verifications(self) -> List[Dict]:
        """
        Получение списка отложенных верификаций
        
        Returns:
            Список словарей с данными верификаций
        """
        try:
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT document_id, pin_code, created_at 
                FROM pending_verifications
                WHERE synced = 0
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'document_id': row[0],
                    'pin_code': row[1],
                    'created_at': row[2]
                }
                for row in rows
            ]
        except Exception as e:
            Logger.error(f"OfflineCache: Ошибка получения отложенных верификаций: {e}")
            return []
    
    def mark_synced(self, document_id: str):
        """
        Отметка документа как синхронизированного
        
        Args:
            document_id: ID документа
        """
        try:
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE pending_verifications
                SET synced = 1
                WHERE document_id = ? AND synced = 0
            ''', (document_id,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            Logger.error(f"OfflineCache: Ошибка отметки синхронизации: {e}")
    
    def clear_old_cache(self, days=30):
        """
        Очистка старого кэша
        
        Args:
            days: Количество дней для хранения кэша
        """
        try:
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                DELETE FROM cached_documents
                WHERE cached_at < ?
            ''', (cutoff_date,))
            
            cursor.execute('''
                DELETE FROM pending_verifications
                WHERE synced = 1 AND created_at < ?
            ''', (cutoff_date,))
            
            conn.commit()
            conn.close()
            Logger.info(f"OfflineCache: Старый кэш очищен (старше {days} дней)")
        except Exception as e:
            Logger.error(f"OfflineCache: Ошибка очистки кэша: {e}")

