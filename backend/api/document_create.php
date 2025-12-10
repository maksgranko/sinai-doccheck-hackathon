<?php
declare(strict_types=1);
require_once __DIR__ . '/bootstrap.php';

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST') {
    json_response(['status' => 'error', 'message' => 'Method not allowed'], 405);
}

$data = read_json_body();
if (empty($data['internal_code'])) {
    json_response(['status' => 'error', 'message' => 'internal_code обязателен'], 400);
}

$pdo = db();
$publicCode = issue_unique_code($pdo);
$pinHash = hash_pin($data['pin'] ?? null);

$stmt = $pdo->prepare(
    'INSERT INTO documents 
    (public_code, internal_code, document_type, issuer, issue_date, expiry_date, status, metadata, pin_hash)
    VALUES 
    (:public_code, :internal_code, :document_type, :issuer, :issue_date, :expiry_date, :status, :metadata, :pin_hash)'
);

$stmt->execute([
    ':public_code' => $publicCode,
    ':internal_code' => $data['internal_code'],
    ':document_type' => $data['document_type'] ?? null,
    ':issuer' => $data['issuer'] ?? null,
    ':issue_date' => $data['issue_date'] ?? null,
    ':expiry_date' => $data['expiry_date'] ?? null,
    ':status' => $data['status'] ?? 'valid',
    ':metadata' => isset($data['metadata']) ? json_encode($data['metadata'], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) : null,
    ':pin_hash' => $pinHash,
]);

json_response([
    'status' => 'ok',
    'data' => [
        'public_code' => $publicCode,
        'internal_code' => $data['internal_code'],
    ],
], 201);


