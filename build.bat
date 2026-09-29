@echo off
setlocal enabledelayedexpansion
title RoboDrone Launcher & Setup

echo ======================================================
echo                RoboDrone Operations Console
echo ======================================================
echo.

:: 1. Verify Python Installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python is not detected in your PATH.
    echo [*] Launching DRONE__OPS.html directly in default browser...
    start "" "DRONE__OPS.html"
    goto end
)

:: 2. Optional: Install dependencies if requirements.txt exists and is non-empty
if exist requirements.txt (
    for %%A in (requirements.txt) do (
        if %%~zA GTR 0 (
            echo [*] Installing dependencies from requirements.txt...
            python -m pip install -r requirements.txt --quiet
        )
    )
)

:: 3. Launch Drone Operations Console
if exist run_drone_ops.py (
    echo [*] Starting via Python runner...
    python run_drone_ops.py
) else if exist DRONE__OPS.html (
    echo [*] Opening DRONE__OPS.html directly...
    start "" "DRONE__OPS.html"
) else (
    echo [!] Error: DRONE__OPS.html or run_drone_ops.py not found in the current directory.
    pause
    exit /b 1
)

:end
echo.
echo [*] RoboDrone initialization complete.
pause
