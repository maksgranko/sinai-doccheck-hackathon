#!/bin/bash
# Скрипт для патчинга рецепта cryptography в Dockerfile
# Выполняется при сборке образа

set -e

echo "[DOCKER PATCH] Patching cryptography recipe..."

# Ждем, пока python-for-android будет клонирован (может быть в разных местах)
P4A_PATHS=(
    "/app/.buildozer/android/platform/python-for-android"
    "/root/.buildozer/android/platform/python-for-android"
)

P4A_PATH=""
for path in "${P4A_PATHS[@]}"; do
    if [ -d "$path" ]; then
        P4A_PATH="$path"
        break
    fi
done

if [ -z "$P4A_PATH" ]; then
    echo "[DOCKER PATCH] python-for-android not found, will patch later"
    exit 0
fi

CRYPTO_FILE="$P4A_PATH/pythonforandroid/recipes/cryptography/__init__.py"

if [ ! -f "$CRYPTO_FILE" ]; then
    echo "[DOCKER PATCH] Cryptography recipe file not found: $CRYPTO_FILE"
    exit 0
fi

# Проверяем, есть ли уже экспорт
if grep -q "recipe = " "$CRYPTO_FILE" || grep -q "recipe=" "$CRYPTO_FILE"; then
    echo "[DOCKER PATCH] Recipe export already exists"
    exit 0
fi

# Ищем класс рецепта
CLASS_NAME=$(grep -oP 'class\s+\K\w+Recipe' "$CRYPTO_FILE" | head -1)

if [ -z "$CLASS_NAME" ]; then
    echo "[DOCKER PATCH] Could not find recipe class in file"
    exit 1
fi

echo "[DOCKER PATCH] Found class: $CLASS_NAME"

# Добавляем экспорт в конец файла
echo "" >> "$CRYPTO_FILE"
echo "# Экспорт экземпляра рецепта (добавлено автоматически)" >> "$CRYPTO_FILE"
echo "recipe = $CLASS_NAME()" >> "$CRYPTO_FILE"

echo "[DOCKER PATCH] Successfully patched cryptography recipe file"

# Проверяем
if grep -q "recipe = " "$CRYPTO_FILE"; then
    echo "[DOCKER PATCH] Verification: recipe export found in file"
    exit 0
else
    echo "[DOCKER PATCH] ERROR: recipe export not found after patching!"
    exit 1
fi

