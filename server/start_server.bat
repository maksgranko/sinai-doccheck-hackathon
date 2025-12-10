@echo off
REM Скрипт для запуска FastAPI сервера на Windows
echo ========================================
echo Запуск Document Verifier API Server
echo ========================================

cd /d %~dp0

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.10 или выше
    pause
    exit /b 1
)

REM Проверка наличия виртуального окружения
if not exist "venv\" (
    echo Создание виртуального окружения...
    python -m venv venv
)

REM Активация виртуального окружения
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Установка зависимостей
echo Установка зависимостей...
pip install -r requirements.txt

REM Запуск сервера
echo ========================================
echo Запуск сервера на http://0.0.0.0:8000
echo API документация: http://localhost:8000/docs
echo ========================================
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause

