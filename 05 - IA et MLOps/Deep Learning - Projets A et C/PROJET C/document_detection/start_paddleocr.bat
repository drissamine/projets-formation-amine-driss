@echo off
chcp 65001 >nul
title Document OCR API v3.0 - PaddleOCR
cd /d "%~dp0"

echo ============================================================
echo   Document OCR API v3.0 - PaddleOCR Edition
echo ============================================================
echo.
echo [1/4] Installing PaddleOCR if needed...
pip install paddlepaddle paddleocr -q 2>nul

echo [2/4] Checking Python...
python --version

echo [3/4] Starting API server...
echo.
echo   URL: http://localhost:8000
echo   Dashboard: http://localhost:8000/dashboard
echo   Health: http://localhost:8000/health
echo.

python -m uvicorn api.main_paddleocr:app --host 0.0.0.0 --port 8000 --reload

pause