<?php
/**
 * Генерация безопасных публичных кодов и вычисление статуса документа.
 */

declare(strict_types=1);

/**
 * Base64url без паддинга.
 */
function base64url_encode(string $bytes): string
{
    return rtrim(strtr(base64_encode($bytes), '+/', '-_'), '=');
}

/**
 * Генерация публичного кода фиксированной длины.
 */
function generate_public_code(int $length = 22): string
{
    $rawLength = max(16, (int) ceil($length * 0.75));
    $code = base64url_encode(random_bytes($rawLength));
    return substr($code, 0, $length);
}

/**
 * Определение статуса документа по срокам и флагам.
 */
function determine_status(array $document): string
{
    $status = $document['status'] ?? 'invalid';

    if (in_array($status, ['revoked', 'invalid'], true)) {
        return 'invalid';
    }

    if ($status === 'valid') {
        if (!empty($document['expiry_date'])) {
            try {
                $expiry = new DateTime($document['expiry_date']);
                $today = new DateTime('today');
                $days = (int) $today->diff($expiry)->format('%r%a');

                if ($days < 0) {
                    return 'invalid';
                }
                if ($days <= 30) {
                    return 'warning';
                }
            } catch (Exception $e) {
                // Если дата некорректна, считаем документ недействительным
                return 'invalid';
            }
        }
        return 'valid';
    }

    if ($status === 'warning') {
        return 'warning';
    }

    return 'invalid';
}


