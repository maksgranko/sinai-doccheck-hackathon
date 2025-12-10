# Настройка MySQL для Document Verifier

## Обновленные файлы

Все файлы обновлены для работы с MySQL вместо PostgreSQL:

### 1. Конфигурация (`server/app/config.py`)
- Изменен `DATABASE_URL` на MySQL формат
- Обновлены параметры подключения:
  - Host: `195.209.210.97`
  - Port: `3306`
  - Database: `sinai_hackat`
  - User: `sinai_hackat`
  - Password: `^R6E=>k[\OVxT?l*`

### 2. Зависимости (`server/requirements.txt`)
- Удален `psycopg2-binary` (PostgreSQL драйвер)
- Удален `asyncpg` (PostgreSQL async драйвер)
- Добавлен `pymysql` (MySQL драйвер)

### 3. Миграции (`server/migrations/versions/001_initial.py`)
- Заменен `postgresql.JSON` на `sa.JSON()` (MySQL поддерживает JSON)
- Заменен `postgresql.INET` на `sa.String(45)` (для IPv6)
- Изменены типы дат/времени для MySQL

### 4. Модели (`server/app/models/document.py`)
- Убрано `timezone=True` из `DateTime` (MySQL TIMESTAMP не поддерживает timezone)

### 5. Подключение к БД (`server/app/database.py`)
- Добавлен `pool_recycle=3600` для переподключения MySQL

## Установка зависимостей

```bash
cd server
pip install -r requirements.txt
```

## Создание базы данных

База данных уже создана через скрипт `create_database.py` в корне проекта.

Если нужно пересоздать:

```bash
python create_database.py
```

## Запуск сервера

```bash
cd server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Или:

```bash
cd server
python -m app.main
```

## Проверка работы

1. Проверьте подключение к БД:
   ```bash
   curl http://localhost:8000/health
   ```

2. Проверьте API документацию:
   ```
   http://localhost:8000/docs
   ```

3. Проверьте верификацию документа:
   ```bash
   curl -X POST "http://localhost:8000/v1/documents/verify" \
     -H "Content-Type: application/json" \
     -d '{"document_id": "DOC-2024-001"}'
   ```

## Структура БД

### Таблица `documents`
- `id` - INT PRIMARY KEY AUTO_INCREMENT
- `document_id` - VARCHAR(255) UNIQUE NOT NULL
- `document_type` - VARCHAR(100)
- `issuer` - VARCHAR(255)
- `issue_date` - DATE
- `expiry_date` - DATE
- `status` - VARCHAR(20) NOT NULL (valid, warning, invalid, revoked)
- `metadata` - JSON
- `created_at` - TIMESTAMP
- `updated_at` - TIMESTAMP

### Таблица `verifications`
- `id` - INT PRIMARY KEY AUTO_INCREMENT
- `document_id` - VARCHAR(255) NOT NULL
- `user_id` - INT NULL
- `status` - VARCHAR(20) NOT NULL
- `ip_address` - VARCHAR(45) NULL
- `user_agent` - TEXT NULL
- `verified_at` - TIMESTAMP

## Переменные окружения

Создайте файл `.env` в папке `server/` (если нужно переопределить настройки):

```env
DATABASE_URL=mysql+pymysql://sinai_hackat:^R6E=>k[\OVxT?l*@195.209.210.97:3306/sinai_hackat?charset=utf8mb4
DB_HOST=195.209.210.97
DB_PORT=3306
DB_NAME=sinai_hackat
DB_USER=sinai_hackat
DB_PASSWORD=^R6E=>k[\OVxT?l*
```

## Важные замечания

1. **Пароль содержит спецсимволы** - убедитесь, что они правильно экранированы в URL
2. **Кодировка** - используется `utf8mb4` для поддержки эмодзи и всех Unicode символов
3. **Пулы соединений** - MySQL требует периодического переподключения (`pool_recycle=3600`)
4. **JSON** - MySQL 5.7+ поддерживает нативный тип JSON

## Тестовые документы

В БД уже есть тестовые документы:
- `DOC-2024-001` - Валидный паспорт
- `DOC-2024-002` - Валидное водительское удостоверение
- `DOC-2024-003` - Медицинская справка (warning - истекает скоро)
- `DOC-2024-004` - Справка о доходах (invalid - истек срок)
- И другие...

Используйте их для тестирования API.

