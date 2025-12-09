"""
Конфигурация приложения
"""
import os

# URL API сервера
# Для использования mock сервера установите: API_BASE_URL = "http://localhost:8000"
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://api.document-verifier.ru/v1"
)

# Использование mock сервера (для разработки)
USE_MOCK_SERVER = os.getenv("USE_MOCK_SERVER", "false").lower() == "true"

if USE_MOCK_SERVER:
    API_BASE_URL = "http://localhost:8000/v1"



