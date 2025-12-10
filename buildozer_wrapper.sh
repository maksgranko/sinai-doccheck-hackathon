#!/bin/bash
# Wrapper для buildozer, который патчит python-for-android ПЕРЕД запуском

set -e

echo "============================================================"
echo "[WRAPPER] Buildozer wrapper starting..."
echo "============================================================"

# Ждем, пока python-for-android будет клонирован
echo "[WRAPPER] Waiting for python-for-android to be cloned..."
MAX_WAIT=60
P4A_FOUND=0
for i in $(seq 1 $MAX_WAIT); do
    if [ -d "/app/.buildozer/android/platform/python-for-android" ] || [ -d "/root/.buildozer/android/platform/python-for-android" ]; then
        echo "[WRAPPER] python-for-android found after $i seconds!"
        P4A_FOUND=1
        sleep 2  # Ожидание для завершения записи файлов
        break
    fi
    sleep 1
done

if [ $P4A_FOUND -eq 0 ]; then
    echo "[WARNING] python-for-android not found after $MAX_WAIT seconds, continuing anyway..."
fi

# Применяем патч ОДИН РАЗ
if [ $P4A_FOUND -eq 1 ]; then
    echo "[WRAPPER] Applying patch to cryptography recipe..."
    /app/patch_crypto_in_docker.sh 2>&1 || true
fi

echo "============================================================"
echo "[WRAPPER] Starting buildozer..."
echo "============================================================"

# Запускаем buildozer
exec buildozer "$@"
