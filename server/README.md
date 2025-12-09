# Серверная часть - Document Verifier API

## Быстрый старт

### Локальная разработка

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл

# Запуск миграций
alembic upgrade head

# Запуск сервера
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker развертывание

```bash
docker-compose up -d
```

## Структура проекта

См. `TECH_STACK.md` для полной структуры.

## API документация

После запуска сервера доступна автоматическая документация:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Переменные окружения

См. `.env.example` для примера конфигурации.

## Развертывание на продакшн

См. `TECH_STACK.md` раздел "Развертывание сервера".


