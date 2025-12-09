"""
Безопасное хранение PIN-кода
"""
import json
from pathlib import Path
from typing import Optional
from kivy.logger import Logger
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os


class PinStorage:
    """Класс для безопасного хранения PIN-кода"""
    
    def __init__(self, storage_path: str = "secure_storage.json"):
        """
        Инициализация хранилища
        
        Args:
            storage_path: Путь к файлу хранилища
        """
        self.storage_path = Path(storage_path)
        self._key = self._get_or_create_key()
        self.cipher = Fernet(self._key)
    
    def _get_or_create_key(self) -> bytes:
        """
        Получение или создание ключа шифрования
        
        Returns:
            Ключ шифрования
        """
        key_file = Path("encryption.key")
        
        if key_file.exists():
            try:
                return key_file.read_bytes()
            except Exception as e:
                Logger.error(f"PinStorage: Ошибка чтения ключа: {e}")
        
        # Создание нового ключа
        key = Fernet.generate_key()
        try:
            key_file.write_bytes(key)
            Logger.info("PinStorage: Создан новый ключ шифрования")
        except Exception as e:
            Logger.error(f"PinStorage: Ошибка сохранения ключа: {e}")
        
        return key
    
    def save_pin(self, pin: str) -> bool:
        """
        Сохранение PIN-кода в зашифрованном виде
        
        Args:
            pin: PIN-код для сохранения
            
        Returns:
            True если успешно
        """
        try:
            encrypted_pin = self.cipher.encrypt(pin.encode())
            
            data = {
                'pin': base64.b64encode(encrypted_pin).decode()
            }
            
            self.storage_path.write_text(json.dumps(data))
            Logger.info("PinStorage: PIN-код сохранен")
            return True
        except Exception as e:
            Logger.error(f"PinStorage: Ошибка сохранения PIN: {e}")
            return False
    
    def get_pin(self) -> Optional[str]:
        """
        Получение расшифрованного PIN-кода
        
        Returns:
            PIN-код или None
        """
        try:
            if not self.storage_path.exists():
                return None
            
            data = json.loads(self.storage_path.read_text())
            encrypted_pin = base64.b64decode(data['pin'])
            pin = self.cipher.decrypt(encrypted_pin).decode()
            
            return pin
        except Exception as e:
            Logger.error(f"PinStorage: Ошибка получения PIN: {e}")
            return None
    
    def has_pin(self) -> bool:
        """
        Проверка наличия сохраненного PIN-кода
        
        Returns:
            True если PIN сохранен
        """
        return self.storage_path.exists() and self.get_pin() is not None
    
    def delete_pin(self) -> bool:
        """
        Удаление сохраненного PIN-кода
        
        Returns:
            True если успешно
        """
        try:
            if self.storage_path.exists():
                self.storage_path.unlink()
                Logger.info("PinStorage: PIN-код удален")
            return True
        except Exception as e:
            Logger.error(f"PinStorage: Ошибка удаления PIN: {e}")
            return False

