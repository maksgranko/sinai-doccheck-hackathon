<?php
declare(strict_types=1);
require_once __DIR__ . '/bootstrap.php';

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST') {
    json_response(['status' => 'error', 'message' => 'Method not allowed'], 405);
}

$data = read_json_body();
$publicCode = $data['public_code'] ?? null;

if (!$publicCode) {
    json_response(['status' => 'error', 'message' => 'public_code обязателен'], 400);
}

$pdo = db();
$doc = fetch_document_by_code($pdo, $publicCode);
if (!$doc) {
    json_response(['status' => 'error', 'message' => 'Не является документом'], 404);
}

$newCode = issue_unique_code($pdo);
$stmt = $pdo->prepare('UPDATE documents SET public_code = :new_code, updated_at = NOW() WHERE id = :id');
$stmt->execute([
    ':new_code' => $newCode,
    ':id' => $doc['id'],
]);

json_response([
    'status' => 'ok',
    'data' => [
        'old_public_code' => $publicCode,
        'public_code' => $newCode,
    ],
]);


