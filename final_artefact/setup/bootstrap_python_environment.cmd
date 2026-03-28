@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap_python_environment.ps1"
exit /b %ERRORLEVEL%