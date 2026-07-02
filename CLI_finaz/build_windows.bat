@echo off
setlocal

echo === financ-app Windows Build ===

where pyinstaller >nul 2>nul
if errorlevel 1 (
    pip install pyinstaller
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller financ-app.spec
if errorlevel 1 exit /b 1

echo.
echo Fertig! Binary liegt unter: dist\financ-app.exe
