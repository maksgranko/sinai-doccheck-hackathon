"""
Конфигурация приложения
"""
import os

# Базовый URL внешнего PHP API (без прямого доступа к БД)
API_BASE_URL = os.getenv("API_BASE_URL", "http://195.209.210.97:7777/sinai.hackathon")

# Пути эндпоинтов
API_VERIFY_PATH = os.getenv("API_VERIFY_PATH", "/api/verify.php")
API_DOCUMENT_PATH = os.getenv("API_DOCUMENT_PATH", "/api/document.php")  # GET /?public_code=

# HTTP таймауты и ретраи
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10.0"))  # seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))



