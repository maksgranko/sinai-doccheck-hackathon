#!/bin/bash
# Скрипт для запуска FastAPI сервера на Linux/Mac

echo "========================================"
echo "Запуск Document Verifier API Server"
echo "========================================"

cd "$(dirname "$0")"

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "ОШИБКА: Python3 не найден!"
    echo "Установите Python 3.10 или выше"
    exit 1
fi

# Проверка наличия виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "Установка зависимостей..."
pip install -r requirements.txt

# Запуск сервера
echo "========================================"
echo "Запуск сервера на http://0.0.0.0:8000"
echo "API документация: http://localhost:8000/docs"
echo "========================================"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

