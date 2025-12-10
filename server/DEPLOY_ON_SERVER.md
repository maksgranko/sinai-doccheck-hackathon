# Развертывание API сервера на удаленном сервере

## Сервер: 195.209.210.97

## Что нужно сделать на сервере:

### 1. Подключитесь к серверу по SSH

```bash
ssh user@195.209.210.97
```

### 2. Установите зависимости

```bash
# Перейдите в директорию с проектом
cd /path/to/server

# Установите Python зависимости
pip install -r requirements.txt

# Или используйте venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Запустите API сервер

```bash
# Запуск на порту 8000
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Откройте порт 8000 в firewall

```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp

# CentOS/RHEL
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload
```

### 5. Автозапуск через systemd (опционально)

Создайте файл `/etc/systemd/system/document-verifier-api.service`:

```ini
[Unit]
Description=Document Verifier API
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/server
Environment="PATH=/path/to/server/venv/bin"
ExecStart=/path/to/server/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация:
```bash
sudo systemctl daemon-reload
sudo systemctl enable document-verifier-api
sudo systemctl start document-verifier-api
sudo systemctl status document-verifier-api
```

## Проверка работы:

```bash
# Health check
curl http://195.209.210.97:8000/health

# Верификация документа
curl "http://195.209.210.97:8000/v1/documents/verify?document_id=DOC-2024-001"
```

## Конфигурация:

API сервер автоматически подключится к MySQL БД:
- Host: `195.209.210.97:3306`
- Database: `sinai_hackat`
- User: `sinai_hackat`
- Password: `^R6E=>k[\OVxT?l*`

Настройки в `server/app/config.py` уже правильные.

## После запуска:

Приложение будет обращаться к `http://195.209.210.97:8000/v1` и получать данные из БД.

