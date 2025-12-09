@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo   Environment Check
echo ========================================
echo.

echo [CHECK] Current directory:
cd
echo.

echo [CHECK] Python:
python --version 2>nul
if errorlevel 1 echo [ERROR] Python not found!
echo.

echo [CHECK] Docker:
docker --version 2>nul
if errorlevel 1 (
    echo [ERROR] Docker not found!
) else (
    echo [OK] Docker found
    docker ps >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker is not running!
    ) else (
        echo [OK] Docker is running
    )
)
echo.

echo [CHECK] Files:
if exist "buildozer.spec" (
    echo [OK] buildozer.spec found
) else (
    echo [ERROR] buildozer.spec not found!
)

if exist "Dockerfile.buildozer" (
    echo [OK] Dockerfile.buildozer found
) else (
    echo [ERROR] Dockerfile.buildozer not found!
)

if exist "requirements.txt" (
    echo [OK] requirements.txt found
) else (
    echo [ERROR] requirements.txt not found!
)
echo.

echo [CHECK] Disk space:
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do echo Free space: %%a bytes
echo.

pause

