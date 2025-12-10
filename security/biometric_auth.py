"""
Модуль биометрической аутентификации
"""
import platform
from kivy.logger import Logger
from typing import Optional, Callable

# Попытка импорта биометрии из plyer
try:
    from plyer import biometric
    BIOMETRIC_AVAILABLE = True
except (ImportError, AttributeError):
    # Биометрия недоступна на Windows или не установлена
    biometric = None
    BIOMETRIC_AVAILABLE = False
    if platform.system() == 'Windows':
        Logger.info("BiometricAuth: Биометрия недоступна на Windows (только Android/iOS)")
    else:
        Logger.warning("BiometricAuth: Модуль biometric недоступен в plyer")


class BiometricAuth:
    """Класс для работы с биометрической аутентификацией"""
    
    def __init__(self):
        """Инициализация модуля биометрии"""
        self.is_available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """
        Проверка доступности биометрической аутентификации
        
        Returns:
            True если доступна
        """
        if not BIOMETRIC_AVAILABLE or biometric is None:
            return False
        
        if platform.system() == 'Windows':
            # Биометрия не поддерживается на Windows через plyer
            return False
        
        try:
            return biometric.is_available()
        except Exception as e:
            Logger.warning(f"BiometricAuth: Биометрия недоступна: {e}")
            return False
    
    def authenticate(
        self, 
        reason: str = "Требуется аутентификация для доступа к журналу",
        callback: Optional[Callable[[bool], None]] = None
    ) -> bool:
        """
        Выполнение биометрической аутентификации
        
        Args:
            reason: Причина запроса аутентификации
            callback: Функция обратного вызова (success: bool)
            
        Returns:
            True если аутентификация успешна
        """
        if not self.is_available or biometric is None:
            Logger.warning("BiometricAuth: Биометрия недоступна")
            if callback:
                callback(False)
            return False
        
        try:
            result = biometric.authenticate(reason=reason)
            if callback:
                callback(result)
            return result
        except Exception as e:
            Logger.error(f"BiometricAuth: Ошибка аутентификации: {e}")
            if callback:
                callback(False)
            return False
    
    def get_biometric_type(self) -> str:
        """
        Получение типа биометрии
        
        Returns:
            Тип биометрии ('face', 'fingerprint', 'iris' или 'unknown')
        """
        try:
            if self.is_available:
                # Попытка определить тип (plyer может не поддерживать напрямую)
                return "fingerprint"  # По умолчанию
        except:
            pass
        return "unknown"



