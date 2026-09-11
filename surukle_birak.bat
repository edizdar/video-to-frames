@echo off
chcp 65001 >nul
title Video to Photos - Video Kare Yakalayici

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if "%~1"=="" (
    python cli.py
) else (
    python cli.py "%~1"
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo Bir hata olustu veya Python calistirilamadi.
    pause
)
