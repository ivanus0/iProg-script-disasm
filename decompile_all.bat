@echo off
cd /d "%~dp0"

if "%~1"=="" (
    py iProgDecompiler.py
) else (
    py iProgDecompiler.py "%~1"
)

pause