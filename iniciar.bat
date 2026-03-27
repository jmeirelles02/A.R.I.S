@echo off
start /b python main.py
timeout /t 3 /nobreak >nul
cd Agent-ui
npm run tauri dev