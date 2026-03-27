@echo off
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)
start /b python main.py
timeout /t 3 /nobreak >nul
cd Agent-ui
npm run tauri dev