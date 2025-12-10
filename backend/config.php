<?php

return [
    'db' => [
        'host' => getenv('DB_HOST') ?: 'localhost',
        'port' => getenv('DB_PORT') ?: '3306',
        'name' => getenv('DB_NAME') ?: 'sinai_hackat',
        'user' => getenv('DB_USER') ?: 'sinai_hackat',
        'pass' => getenv('DB_PASSWORD') ?: '^R6E=>k[\OVxT?l*',
        'charset' => 'utf8mb4',
    ],
    'app_secret' => getenv('APP_SECRET') ?: 'APP_SECRET_CODE',
];


