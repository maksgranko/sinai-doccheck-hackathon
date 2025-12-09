-- Инициализация базы данных для Document Verifier

-- Создание базы данных (выполнить от пользователя postgres)
-- CREATE DATABASE document_verifier;

-- Подключение к базе данных document_verifier
-- \c document_verifier

-- Создание таблицы документов
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) UNIQUE NOT NULL,
    document_type VARCHAR(100),
    issuer VARCHAR(255),
    issue_date DATE,
    expiry_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'valid',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для таблицы documents
CREATE INDEX IF NOT EXISTS idx_document_id ON documents(document_id);
CREATE INDEX IF NOT EXISTS idx_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_expiry_date ON documents(expiry_date);

-- Создание таблицы верификаций
CREATE TABLE IF NOT EXISTS verifications (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    user_id INTEGER,
    status VARCHAR(20) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

-- Индексы для таблицы verifications
CREATE INDEX IF NOT EXISTS idx_verifications_document ON verifications(document_id);
CREATE INDEX IF NOT EXISTS idx_verifications_date ON verifications(verified_at);

-- Вставка тестовых данных
INSERT INTO documents (document_id, document_type, issuer, issue_date, expiry_date, status, metadata) VALUES
('DOC001', 'Справка', 'Госструктура', '2024-01-15', '2025-01-15', 'valid', '{}'),
('DOC002', 'Сертификат', 'Банк', '2023-06-01', CURRENT_DATE + INTERVAL '10 days', 'warning', '{"warning": "Срок действия истекает через 10 дней"}'),
('DOC003', 'Справка', 'Организация', '2023-01-01', '2024-01-01', 'invalid', '{"error": "Документ отозван"}')
ON CONFLICT (document_id) DO NOTHING;

-- Комментарии к таблицам
COMMENT ON TABLE documents IS 'Таблица документов в реестре';
COMMENT ON TABLE verifications IS 'Журнал верификаций документов';
COMMENT ON COLUMN documents.status IS 'Статус: valid, warning, invalid, revoked';
COMMENT ON COLUMN verifications.status IS 'Результат верификации: valid, warning, invalid';


