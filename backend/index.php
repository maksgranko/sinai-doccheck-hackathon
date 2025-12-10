<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-PIN-Code');

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'OPTIONS') {
    http_response_code(204);
    exit;
}

http_response_code(404);
echo json_encode([
    'status' => 'error',
    'message' => 'Используйте /api/verify.php, /api/document.php, /api/document_create.php, /api/document_rotate.php'
], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);