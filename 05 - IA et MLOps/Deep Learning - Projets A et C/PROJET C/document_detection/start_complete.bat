@echo off
chcp 65001 >nul
title Document OCR API v2.0
cd /d "%~dp0"

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                                                                    ║
echo ║          Document OCR API v2.0 - Improved                          ║
echo ║                                                                    ║
echo ║  Features:                                                         ║
echo ║  - Smart preprocessing for low-quality photos                    ║
echo ║  - EasyOCR + Tesseract dual engine                               ║
echo ║  - Field extraction (Name, DOB, Numbers, etc.)                   ║
echo ║  - Web dashboard with drag-and-drop                              ║
echo ║                                                                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Check Python
echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)
echo     Python OK
echo.

REM Check dependencies
echo [2/3] Checking dependencies...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo     Installing dependencies...
    pip install -r requirements.txt -q
) else (
    echo     Dependencies OK
)
echo.

REM Start API
echo [3/3] Starting API server...
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║  API URL: http://localhost:8000                                  ║
echo ║  Dashboard: http://localhost:8000/dashboard                       ║
echo ║  Health: http://localhost:8000/health                            ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn api.main_improved:app --host 0.0.0.0 --port 8000 --reload

pause
