@echo off
chcp 65001 >nul
title Manager AI PRO
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
python manager_ai_pro.py
if errorlevel 1 (
    echo.
    pause
)
