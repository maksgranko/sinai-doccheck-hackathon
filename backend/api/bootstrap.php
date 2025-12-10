<?php
/**
 * Общий bootstrap для всех эндпоинтов API.
 */
declare(strict_types=1);

require_once __DIR__ . '/../db.php';
require_once __DIR__ . '/../helpers/code.php';

// Базовые заголовки
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-PIN-Code');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

function json_response(array $payload, int $status = 200): void
{
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function read_json_body(): array
{
    $raw = file_get_contents('php://input');
    if ($raw === false || $raw === '') {
        return [];
    }
    $data = json_decode($raw, true);
    return is_array($data) ? $data : [];
}

function normalize_metadata($value)
{
    if (is_array($value)) {
        return $value;
    }
    if (is_string($value) && $value !== '') {
        $decoded = json_decode($value, true);
        return $decoded === null ? $value : $decoded;
    }
    return null;
}

function hash_pin(?string $pin): ?string
{
    if (!$pin) {
        return null;
    }
    if (defined('PASSWORD_ARGON2ID')) {
        return password_hash($pin, PASSWORD_ARGON2ID);
    }
    return password_hash($pin, PASSWORD_BCRYPT);
}

function verify_pin_if_needed(array $document, ?string $pin): void
{
    if (!empty($document['pin_hash'])) {
        if (!$pin || !password_verify($pin, $document['pin_hash'])) {
            json_response([
                'status' => 'error',
                'message' => 'Неверный PIN или не указан',
            ], 401);
        }
    }
}

function log_verification(PDO $pdo, int $documentId, string $publicCode, string $status): void
{
    $stmt = $pdo->prepare(
        'INSERT INTO verifications (document_id, public_code_used, status, ip_address, user_agent) 
         VALUES (:document_id, :public_code_used, :status, :ip, :ua)'
    );
    $stmt->execute([
        ':document_id' => $documentId,
        ':public_code_used' => $publicCode,
        ':status' => $status,
        ':ip' => $_SERVER['REMOTE_ADDR'] ?? null,
        ':ua' => $_SERVER['HTTP_USER_AGENT'] ?? null,
    ]);
}

function issue_unique_code(PDO $pdo, int $length = 22): string
{
    for ($i = 0; $i < 5; $i++) {
        $code = generate_public_code($length);
        $exists = $pdo->prepare('SELECT 1 FROM documents WHERE public_code = :code LIMIT 1');
        $exists->execute([':code' => $code]);
        if ($exists->fetchColumn() === false) {
            return $code;
        }
    }
    json_response([
        'status' => 'error',
        'message' => 'Не удалось сгенерировать уникальный код',
    ], 500);
}

function fetch_document_by_code(PDO $pdo, string $publicCode): ?array
{
    $stmt = $pdo->prepare(
        'SELECT id, public_code, internal_code, document_type, issuer, issue_date, expiry_date, status, metadata, pin_hash 
         FROM documents 
         WHERE public_code = :code
         LIMIT 1'
    );
    $stmt->execute([':code' => $publicCode]);
    $doc = $stmt->fetch();
    if ($doc === false) {
        return null;
    }
    $doc['metadata'] = normalize_metadata($doc['metadata']);
    return $doc;
}


