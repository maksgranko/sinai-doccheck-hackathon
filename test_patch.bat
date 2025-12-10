@echo off
echo ========================================
echo   Testing patch script
echo ========================================
echo.

REM Check if patch script exists
if not exist "patch_p4a_recipe.py" (
    echo [ERROR] patch_p4a_recipe.py not found!
    pause
    exit /b 1
)

echo [INFO] Running patch script...
python patch_p4a_recipe.py

if errorlevel 1 (
    echo [ERROR] Patch script failed!
    pause
    exit /b 1
)

echo [SUCCESS] Patch script completed successfully!
pause

