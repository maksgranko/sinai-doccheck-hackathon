<?php
declare(strict_types=1);
require_once __DIR__ . '/bootstrap.php';

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'GET') {
    json_response(['status' => 'error', 'message' => 'Method not allowed'], 405);
}

$publicCode = $_GET['public_code'] ?? null;
$pin = $_GET['pin'] ?? null;

if (!$publicCode) {
    json_response(['status' => 'error', 'message' => 'public_code обязателен'], 400);
}

$pdo = db();
$doc = fetch_document_by_code($pdo, $publicCode);
if (!$doc) {
    json_response(['status' => 'error', 'message' => 'Не является документом'], 404);
}

verify_pin_if_needed($doc, $pin);
$resolvedStatus = determine_status($doc);

json_response([
    'status' => 'ok',
    'data' => [
        'public_code' => $doc['public_code'],
        'document_type' => $doc['document_type'],
        'issuer' => $doc['issuer'],
        'issue_date' => $doc['issue_date'],
        'expiry_date' => $doc['expiry_date'],
        'status' => $resolvedStatus,
        'metadata' => $doc['metadata'],
    ],
]);


