@echo off
chcp 65001 >nul
title Video Kare Yakalayici - Arayuz

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

start "" pythonw gui.py
if %ERRORLEVEL% neq 0 (
    python gui.py
)
