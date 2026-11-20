@echo off
cd /d "%~dp0"
python -m uvicorn api.ocr_api:app --port 8000 --host 127.0.0.1