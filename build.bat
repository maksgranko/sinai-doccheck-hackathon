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

REM Build Docker image
echo [INFO] Building Docker image...
echo [INFO] This may take 5-10 minutes on first run...
echo.
docker build -f Dockerfile.buildozer -t buildozer-app .
if errorlevel 1 (
    echo [ERROR] Docker build failed!
    pause
    exit /b 1
)
echo [OK] Docker image ready
echo.

REM Clean cache (optional)
echo [INFO] Clean build cache?
echo [INFO] Keeping cache will make subsequent builds faster
set /p clean_cache="Clean cache? (Y/N, default=N): "
if /i "%clean_cache%"=="Y" (
    echo [INFO] Cleaning cache...
    if exist ".buildozer" (
        rmdir /s /q ".buildozer" 2>nul
        timeout /t 2 >nul
    )
    echo [INFO] Removing problematic build caches...
    docker run --rm -v "%cd%":/app:Z -v "%USERPROFILE%\.buildozer":/root/.buildozer:Z buildozer-app sh -c "rm -rf /app/.buildozer /root/.buildozer/android/platform/build-*/build/other_builds/Pillow 2>/dev/null; echo 'Cache cleaned'"
    echo [OK] Cache cleaned
) else (
    echo [INFO] Keeping cache for faster builds
)
echo.

REM Build APK
echo [INFO] Starting APK build...
echo [INFO] Using ccache for faster compilation...
echo [WARNING] First build may take 30-60 minutes...
echo [INFO] Subsequent builds will be much faster thanks to ccache
echo.
docker run --rm -it ^
    -v "%cd%":/app:Z ^
    -v "%USERPROFILE%\.buildozer":/root/.buildozer:Z ^
    -v "%USERPROFILE%\.ccache":/root/.ccache:Z ^
    -w /app ^
    -e BUILDozer_ALLOW_ROOT=1 ^
    -e LC_ALL=C.UTF-8 ^
    -e LANG=C.UTF-8 ^
    -e PYTHONUNBUFFERED=1 ^
    -e USE_CCACHE=1 ^
    -e CCACHE_DIR=/root/.ccache ^
    -e CCACHE_MAXSIZE=5G ^
    -e NUM_BUILD_CORES=4 ^
    buildozer-app ^
    sh -c "chmod +x /app/buildozer_wrapper.sh && yes | /app/buildozer_wrapper.sh android debug"

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
