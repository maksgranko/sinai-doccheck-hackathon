@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
cls

REM Enable error handling
set "ERROR_OCCURRED=0"

echo ========================================
echo   Building Android APK (Native - No Docker)
echo ========================================
echo.
echo [WARNING] Buildozer on Windows often has issues!
echo [INFO] If this fails, use build.bat (Docker method)
echo.

REM Check Python
echo [CHECK] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo [INFO] Install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo [OK] Python found
echo.

REM Check Java
echo [CHECK] Checking Java...
java -version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Java JDK not found!
    echo [INFO] Install Java JDK 17+ from https://adoptium.net/
    echo [INFO] Add JAVA_HOME to environment variables
    pause
    exit /b 1
)
java -version 2>&1 | findstr /C:"version"
echo [OK] Java found
echo.

REM Check buildozer.spec
if not exist "buildozer.spec" (
    echo [ERROR] buildozer.spec not found!
    pause
    exit /b 1
)
echo [OK] buildozer.spec found
echo.

REM Install/Check Buildozer
echo [CHECK] Checking Buildozer...
python -c "import buildozer" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Buildozer...
    pip install buildozer
    if errorlevel 1 (
        echo [ERROR] Failed to install Buildozer!
        pause
        exit /b 1
    )
)
echo [OK] Buildozer installed
echo.

REM Install/Check python-for-android
echo [CHECK] Checking python-for-android...
python -c "import p4a" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing python-for-android...
    pip install python-for-android
    if errorlevel 1 (
        echo [WARNING] Failed to install python-for-android
        echo [INFO] Will try buildozer directly
    ) else (
        echo [OK] python-for-android installed
    )
) else (
    echo [OK] python-for-android already installed
)
echo.

REM Install requirements (OPTIONAL - skip for Android build)
echo [INFO] Installing Python requirements for Windows...
echo [INFO] NOTE: This step is OPTIONAL for Android build
echo [INFO] Buildozer will handle dependencies automatically
echo.
set /p skip_req="Skip Windows requirements installation? (Y/N, default=Y): "
if /i "%skip_req%"=="N" (
    if exist "requirements.txt" (
        echo [INFO] Installing Kivy dependencies first...
        pip install --upgrade pip setuptools wheel
        if errorlevel 1 (
            echo [WARNING] Failed to upgrade pip, continuing...
        )
        pip install Cython==0.29.33
        if errorlevel 1 (
            echo [WARNING] Failed to install Cython, continuing...
        )
        echo [INFO] Installing kivy_deps (required for Kivy on Windows)...
        pip install kivy_deps.sdl2_dev kivy_deps.gstreamer_dev
        if errorlevel 1 (
            echo [WARNING] kivy_deps installation skipped (not critical for Android build)
        )
        echo [INFO] Installing other requirements...
        echo [INFO] Note: Some packages may fail on Windows - this is OK for Android build
        pip install -r requirements.txt --no-build-isolation
        if errorlevel 1 (
            echo [WARNING] Some requirements failed to install
            echo [INFO] This is OK for Android build - Buildozer will handle dependencies
        )
    ) else (
        echo [WARNING] requirements.txt not found
    )
) else (
    echo [INFO] Skipping Windows requirements installation
    echo [INFO] Buildozer will handle dependencies for Android
)
echo.

REM Clean previous builds
echo [INFO] Cleaning previous builds...
set /p clean_cache="Clean previous build cache? (Y/N, default=Y): "
if /i not "%clean_cache%"=="N" (
    if exist ".buildozer" (
        echo [INFO] Removing .buildozer cache...
        rmdir /s /q ".buildozer" 2>nul
        if errorlevel 1 (
            echo [WARNING] Failed to remove .buildozer, may be in use
        ) else (
            echo [OK] .buildozer removed
        )
    )
    if exist "bin" (
        echo [INFO] Cleaning bin folder...
        del /q "bin\*.apk" 2>nul
    )
    echo [OK] Cleaned
) else (
    echo [INFO] Keeping cache
)
echo.

REM Select build method
echo ========================================
echo   Select build method
echo ========================================
echo 1. Buildozer (recommended)
echo 2. python-for-android directly
echo.
set /p choice="Enter number (1-2, default=1): "

if "%choice%"=="" set choice=1
if "%choice%"=="1" goto :buildozer
if "%choice%"=="2" goto :p4a

echo [ERROR] Invalid choice! Using default (Buildozer)
set choice=1
goto :buildozer

:buildozer
echo.
echo ========================================
echo   Building with Buildozer
echo ========================================
echo.
echo [WARNING] First build may take 30-60 minutes!
echo [INFO] Buildozer will download Android SDK/NDK automatically
echo.
pause

REM Set environment variables
set BUILDozer_ALLOW_ROOT=1
set LC_ALL=C.UTF-8
set LANG=C.UTF-8

REM Try buildozer
echo [INFO] Starting build...
echo [DEBUG] Current directory: %CD%
echo [DEBUG] Python: 
python --version
echo [DEBUG] Buildozer:
python -m buildozer --version
echo.
echo [INFO] Running: python -m buildozer android debug
echo.
python -m buildozer android debug
set BUILD_RESULT=%ERRORLEVEL%
echo.
echo [DEBUG] Build finished with exit code: %BUILD_RESULT%

if %BUILD_RESULT% EQU 0 (
    goto :check_result
) else (
    echo.
    echo [ERROR] Buildozer failed!
    echo.
    echo ========================================
    echo   Common Issues on Windows
    echo ========================================
    echo.
    echo 1. "Unknown command/target android"
    echo    - This is a known Buildozer issue on Windows
    echo    - Solution: Use Docker (build.bat) or WSL2
    echo.
    echo 2. "No module named p4a"
    echo    - python-for-android not installed correctly
    echo    - Try: pip install --upgrade python-for-android
    echo.
    echo 3. Java/JDK issues
    echo    - Set JAVA_HOME environment variable
    echo    - Add %JAVA_HOME%\bin to PATH
    echo.
    echo [RECOMMENDATION] Use build.bat (Docker method) instead
    echo.
    pause
    exit /b 1
)

:p4a
echo.
echo ========================================
echo   Building with python-for-android
echo ========================================
echo.
echo [WARNING] This method is experimental on Windows!
echo.
pause

REM Try python-for-android directly
python -m p4a create ^
    --requirements=python3,kivy==2.2.0,kivymd==1.1.1,requests==2.31.0,pyzbar==0.1.9,Pillow==9.5.0,cryptography==41.0.7,plyer==2.1.0,certifi==2023.11.17,urllib3==2.1.0,android ^
    --arch=arm64-v8a ^
    --name=DocumentVerifier ^
    --package=org.documentverifier ^
    --version=0.1 ^
    --bootstrap=sdl2 ^
    --android-api=30

set BUILD_RESULT=%ERRORLEVEL%

if %BUILD_RESULT% EQU 0 (
    goto :check_result
) else (
    echo.
    echo [ERROR] python-for-android failed!
    echo [RECOMMENDATION] Use build.bat (Docker method) instead
    pause
    exit /b 1
)

:check_result
echo.
echo ========================================
echo   Build result
echo ========================================
echo.

if exist "bin\*.apk" (
    echo [SUCCESS] APK built successfully!
    echo.
    echo APK files:
    dir /b bin\*.apk
    echo.
    echo Files are in folder: bin\
    echo.
    echo [INFO] To install on Android device:
    echo   1. Enable USB Debugging on device
    echo   2. Connect device via USB
    echo   3. Run: adb install bin\documentverifier-*.apk
) else (
    echo [WARNING] Build completed but APK not found
    echo [INFO] Check logs above for errors
    echo [INFO] APK might be in dist\ folder (python-for-android)
    if exist "dist\*.apk" (
        echo.
        echo Found APK in dist folder:
        dir /b dist\*.apk
    )
)

echo.
pause

