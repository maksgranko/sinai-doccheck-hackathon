-- ============================================
-- Скрипт для создания и заполнения БД MySQL
-- База данных: sinai_hackat
-- ============================================

-- Удаление существующих таблиц (если есть)
DROP TABLE IF EXISTS verifications;
DROP TABLE IF EXISTS documents;

-- Создание таблицы documents
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    public_code VARCHAR(64) NOT NULL UNIQUE,
    internal_code VARCHAR(255) NOT NULL UNIQUE,
    document_type VARCHAR(100),
    issuer VARCHAR(255),
    issue_date DATE,
    expiry_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'valid',
    metadata JSON,
    pin_hash VARBINARY(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_public_code (public_code),
    INDEX idx_internal_code (internal_code),
    INDEX idx_status (status),
    INDEX idx_expiry_date (expiry_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Создание таблицы verifications
CREATE TABLE verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    public_code_used VARCHAR(64) NULL,
    status VARCHAR(20) NOT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_verifications_document (document_id),
    INDEX idx_verifications_date (verified_at),
    CONSTRAINT fk_verifications_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Заполнение тестовыми данными
-- ============================================

-- Вставка документов
INSERT INTO documents (public_code, internal_code, document_type, issuer, issue_date, expiry_date, status, metadata, pin_hash) VALUES
-- Валидные документы
('k5JYl9N5X2jcsf2y8Q1wVA', 'DOC-2024-001', 'Паспорт РФ', 'МВД России', '2024-01-15', '2034-01-15', 'valid', JSON_OBJECT('series', '1234', 'number', '567890', 'full_name', 'Иванов Иван Иванович', 'birth_date', '1990-05-20'), NULL),
('zR1H3vB8pQ0aLk7sF5n9eQ', 'DOC-2024-002', 'Водительское удостоверение', 'ГИБДД', '2023-06-20', '2033-06-20', 'valid', JSON_OBJECT('series', 'АБ', 'number', '123456', 'categories', 'B, C'), NULL),
('M9nB7vC5xZ1aS3dF6gH8jK', 'DOC-2024-006', 'СНИЛС', 'ПФР', '2022-03-10', NULL, 'valid', JSON_OBJECT('number', '123-456-789-01'), NULL),

-- Документы с предупреждением (скоро истекает срок)
('U8mC2sR5aX0pVw7dL3t9bN', 'DOC-2024-003', 'Медицинская справка', 'Поликлиника №1', '2024-11-01', '2024-12-31', 'warning', JSON_OBJECT('warning', 'Срок действия истекает через 30 дней', 'doctor', 'Петров П.П.'), NULL),
('R2eT4yU6iO8pA0sD1fG3hJ', 'DOC-2024-007', 'Сертификат вакцинации', 'Минздрав', '2023-12-01', '2024-12-01', 'warning', JSON_OBJECT('warning', 'Срок действия истекает через 30 дней', 'vaccine', 'Спутник V'), NULL),

-- Недействительные документы
('G4hP9kL2sA7vB1cM8eR6tX', 'DOC-2024-004', 'Справка о доходах', 'Налоговая служба', '2023-01-10', '2023-12-31', 'invalid', JSON_OBJECT('error', 'Срок действия документа истек', 'expired_date', '2023-12-31'), NULL),
('Q1wE3rT5yU7iO9pA2sD4fG', 'DOC-2024-005', 'Диплом', 'Университет', '2020-06-15', NULL, 'invalid', JSON_OBJECT('error', 'Документ отозван (подделка)', 'revoked_date', '2024-01-10'), NULL),
('L0kJ9hG8fD7sA6pO5iU4yT', 'DOC-2024-008', 'Справка о несудимости', 'МВД России', '2022-05-01', '2023-05-01', 'invalid', JSON_OBJECT('error', 'Срок действия документа истек'), NULL),
('N7bV5cX3zL1kP9oI8uY6tR', 'DOC-2024-009', 'Трудовая книжка', 'Организация ООО "Рога и Копыта"', '2018-01-01', NULL, 'invalid', JSON_OBJECT('error', 'Документ не найден в реестре'), NULL),

-- Дополнительные тестовые документы
('H6gF4dS2aZ0xC8vB9nM7lK', 'DOC-2024-010', 'Паспорт РФ', 'МВД России', '2023-03-15', '2033-03-15', 'valid', JSON_OBJECT('series', '5678', 'number', '901234', 'full_name', 'Петрова Мария Сергеевна', 'birth_date', '1995-08-12'), NULL),
('T3yR5eW7qU9iO1pA4sD6fG', 'DOC-2024-011', 'Водительское удостоверение', 'ГИБДД', '2024-02-10', '2034-02-10', 'valid', JSON_OBJECT('series', 'ВГ', 'number', '789012', 'categories', 'B'), NULL);

-- Вставка записей верификации
INSERT INTO verifications (document_id, public_code_used, status, ip_address, user_agent, verified_at) VALUES
((SELECT id FROM documents WHERE internal_code = 'DOC-2024-001'), 'k5JYl9N5X2jcsf2y8Q1wVA', 'valid', '192.168.1.100', 'DocumentVerifier/1.0', '2024-12-09 10:30:00'),
((SELECT id FROM documents WHERE internal_code = 'DOC-2024-001'), 'k5JYl9N5X2jcsf2y8Q1wVA', 'valid', '192.168.1.101', 'DocumentVerifier/1.0', '2024-12-09 14:20:00'),
((SELECT id FROM documents WHERE internal_code = 'DOC-2024-002'), 'zR1H3vB8pQ0aLk7sF5n9eQ', 'valid', '192.168.1.102', 'DocumentVerifier/1.0', '2024-12-08 09:15:00'),
((SELECT id FROM documents WHERE internal_code = 'DOC-2024-003'), 'U8mC2sR5aX0pVw7dL3t9bN', 'warning', '192.168.1.103', 'DocumentVerifier/1.0', '2024-12-07 16:45:00'),
((SELECT id FROM documents WHERE internal_code = 'DOC-2024-004'), 'G4hP9kL2sA7vB1cM8eR6tX', 'invalid', '192.168.1.104', 'DocumentVerifier/1.0', '2024-12-06 11:30:00'),
((SELECT id FROM documents WHERE internal_code = 'DOC-2024-005'), 'Q1wE3rT5yU7iO9pA2sD4fG', 'invalid', '192.168.1.105', 'DocumentVerifier/1.0', '2024-12-05 13:20:00'),
((SELECT id FROM documents WHERE internal_code = 'DOC-2024-006'), 'M9nB7vC5xZ1aS3dF6gH8jK', 'valid', '192.168.1.106', 'DocumentVerifier/1.0', '2024-12-04 10:10:00'),
((SELECT id FROM documents WHERE internal_code = 'DOC-2024-007'), 'R2eT4yU6iO8pA0sD1fG3hJ', 'warning', '192.168.1.107', 'DocumentVerifier/1.0', '2024-12-03 15:30:00'),
((SELECT id FROM documents WHERE internal_code = 'DOC-2024-010'), 'H6gF4dS2aZ0xC8vB9nM7lK', 'valid', '192.168.1.108', 'DocumentVerifier/1.0', '2024-12-02 12:00:00'),
((SELECT id FROM documents WHERE internal_code = 'DOC-2024-011'), 'T3yR5eW7qU9iO1pA4sD6fG', 'valid', '192.168.1.109', 'DocumentVerifier/1.0', '2024-12-01 09:45:00');

-- Вывод статистики
SELECT 
    'Документы созданы' AS info,
    COUNT(*) AS count
FROM documents
UNION ALL
SELECT 
    'Верификации созданы' AS info,
    COUNT(*) AS count
FROM verifications
UNION ALL
SELECT 
    'Валидных документов' AS info,
    COUNT(*) AS count
FROM documents
WHERE status = 'valid'
UNION ALL
SELECT 
    'Документов с предупреждением' AS info,
    COUNT(*) AS count
FROM documents
WHERE status = 'warning'
UNION ALL
SELECT 
    'Недействительных документов' AS info,
    COUNT(*) AS count
FROM documents
WHERE status = 'invalid';

-- Показать все документы
SELECT 
    public_code,
    internal_code,
    document_type,
    issuer,
    issue_date,
    expiry_date,
    status,
    created_at
FROM documents
ORDER BY internal_code;

