FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Создание директории для логов
RUN mkdir -p /var/log/document-verifier

# Запуск миграций и сервера
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000


