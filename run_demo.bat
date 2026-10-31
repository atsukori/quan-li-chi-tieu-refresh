@echo off
setlocal
cd /d "%~dp0"
title Group Expense Manager - Demo Data

if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Cannot find the .venv virtual environment.
    echo Run these commands in this project folder first:
    echo   py -3.11 -m venv .venv
    echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

echo.
echo WARNING: Demo mode will DELETE the current database data and recreate demo data.
echo This removes existing accounts, categories, transactions, and budgets.
echo.
choice /C YN /N /M "Continue? Press Y to reset to demo data or N to cancel: "
if errorlevel 2 goto cancelled

echo.
echo Creating demo database...
python seed.py --reset
if errorlevel 1 (
    echo.
    echo ERROR: Demo data initialization failed. The server will not be started.
    pause
    exit /b 1
)

echo.
echo Starting Flask at http://127.0.0.1:5000
python run.py
set "APP_EXIT_CODE=%ERRORLEVEL%"
echo.
echo Flask server has stopped.
pause
exit /b %APP_EXIT_CODE%

:cancelled
echo.
echo Cancelled. No database changes were made.
pause
exit /b 0
