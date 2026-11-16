@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0compress_engine.ps1" "%~1"
pause