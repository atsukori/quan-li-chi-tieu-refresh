@echo off
setlocal
cd /d "%~dp0"
title Group Expense Manager - Admin Only

if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Cannot find the .venv virtual environment.
    echo Run these commands in this project folder first:
    echo   py -3.11 -m venv .venv
    echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

if not exist "instance\family_expenses.db" (
    echo.
    echo Initializing a clean database with one admin account...
    python init_admin.py
    if errorlevel 1 (
        echo.
        echo ERROR: Admin initialization failed. The server will not be started.
        pause
        exit /b 1
    )
) else (
    echo.
    echo Existing database found. Skipping initialization to preserve your data.
    echo If you need to reset to admin-only, run: python init_admin.py --reset
)

echo.
echo Starting Flask at http://127.0.0.1:5000
python run.py
set "APP_EXIT_CODE=%ERRORLEVEL%"
echo.
echo Flask server has stopped.
pause
exit /b %APP_EXIT_CODE%
