@echo off
cd /d "%~dp0"
echo =====================================
echo Document OCR API - Improved v2.0
echo =====================================
echo.
echo Starting improved API with:
echo   - Document detector model
echo   - OCR preprocessing
echo   - EasyOCR support
echo.
cd "%~dp0"
python -m uvicorn api.main_improved:app --reload --port 8000
echo.
pause
