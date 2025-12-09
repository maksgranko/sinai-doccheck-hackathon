@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
cls

echo ========================================
echo   Building Android APK - Document Verifier
echo ========================================
echo.

REM Check Docker
echo [CHECK] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found!
    echo [INFO] Install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo [INFO] Start Docker Desktop and wait until it's ready
    pause
    exit /b 1
)
echo [OK] Docker is ready
echo.

REM Check Dockerfile
if not exist "Dockerfile.buildozer" (
    echo [ERROR] Dockerfile.buildozer not found!
    pause
    exit /b 1
)
echo [OK] Dockerfile.buildozer found
echo.

REM Build Docker image (only if absent)
echo [INFO] Checking buildozer-app image...
docker image inspect buildozer-app >nul 2>&1
if errorlevel 1 (
    echo [INFO] Image not found, building...
    echo [INFO] This may take 5-10 minutes on first run...
    docker build -f Dockerfile.buildozer -t buildozer-app .
    if errorlevel 1 (
        echo [ERROR] Docker build failed!
        pause
        exit /b 1
    )
) else (
    echo [OK] Reusing existing buildozer-app image
)
echo.

REM Build APK
echo [INFO] Starting APK build...
echo [WARNING] This may take 30-60 minutes...
echo.

REM Default: clean cache unless explicitly disabled
if not defined CLEAN_CACHE set CLEAN_CACHE=1

if "%CLEAN_CACHE%"=="1" goto :CLEAN_CACHE_BLOCK
echo [INFO] Skipping cache clean (set CLEAN_CACHE=1 to enable)
goto :AFTER_CLEAN

:CLEAN_CACHE_BLOCK
echo [INFO] Cleaning Pillow recipe cache (to avoid patch mismatch)...
docker run --rm ^
    -v "%cd%":/app:Z ^
    -v "%USERPROFILE%\.buildozer":/root/.buildozer:Z ^
    -w /app ^
    buildozer-app ^
    sh -c "rm -rf /app/.buildozer/android/platform/build-*/build/other_builds/Pillow /root/.buildozer/android/platform/build-*/build/other_builds/Pillow 2>/dev/null || true"
echo [INFO] Cleaning dist cache (to refresh requirements)...
docker run --rm ^
    -v "%cd%":/app:Z ^
    -v "%USERPROFILE%\.buildozer":/root/.buildozer:Z ^
    -w /app ^
    buildozer-app ^
    sh -c "rm -rf /app/.buildozer/android/platform/build-*/dists/documentverifier /root/.buildozer/android/platform/build-*/dists/documentverifier 2>/dev/null || true"
echo [INFO] Cleaning p4a repo (to avoid broken git remote)...
docker run --rm ^
    -v "%cd%":/app:Z ^
    -v "%USERPROFILE%\.buildozer":/root/.buildozer:Z ^
    -w /app ^
    buildozer-app ^
    sh -c "rm -rf /app/.buildozer/android/platform/python-for-android /root/.buildozer/android/platform/python-for-android 2>/dev/null || true"
echo [INFO] Full clean .buildozer (host + container) for fresh recipes...
docker run --rm ^
    -v "%cd%":/app:Z ^
    -v "%USERPROFILE%\.buildozer":/root/.buildozer:Z ^
    -w /app ^
    buildozer-app ^
    sh -c "rm -rf /app/.buildozer /root/.buildozer 2>/dev/null || true"
goto :AFTER_CLEAN

:AFTER_CLEAN

docker run --rm -it ^
    -v "%cd%":/app:Z ^
    -v "%USERPROFILE%\.buildozer":/root/.buildozer:Z ^
    -v "%USERPROFILE%\.gradle":/root/.gradle:Z ^
    -w /app ^
    -e BUILDozer_ALLOW_ROOT=1 ^
    -e LC_ALL=C.UTF-8 ^
    -e LANG=C.UTF-8 ^
    -e PYTHONUNBUFFERED=1 ^
    -e GRADLE_USER_HOME=/root/.gradle ^
    buildozer-app ^
    sh -c "yes | buildozer android debug"

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

REM Check result
if exist "bin\*.apk" (
    echo.
    echo [SUCCESS] APK built successfully!
    echo.
    echo APK files:
    dir /b bin\*.apk
    echo.
    echo Files are in folder: bin\
) else (
    echo.
    echo [WARNING] Build completed but APK not found
    echo [INFO] Check logs above for errors
)

pause
