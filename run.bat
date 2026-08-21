@echo off
REM ===================================================================
REM  AriTyper launcher for Windows (Command Prompt)
REM
REM  Usage:  double-click this file, or from CMD:  run.bat
REM
REM  On first run this creates a private virtual environment and
REM  installs the dependencies. Every run after that just launches
REM  the app, so it starts immediately.
REM ===================================================================
setlocal

cd /d "%~dp0"

set "VENV_DIR=.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "STAMP=%VENV_DIR%\.deps-installed"
set "APP=arityper_activated.py"

echo.
echo  ============================================
echo    AriTyper - free, no license key needed
echo  ============================================
echo.

REM ---- 1. Find a Python interpreter to bootstrap with ----------------
set "BOOT_PY="
py -3 --version >nul 2>&1 && set "BOOT_PY=py -3"
if not defined BOOT_PY (
    python --version >nul 2>&1 && set "BOOT_PY=python"
)

if not defined BOOT_PY (
    echo  [ERROR] Python was not found on this computer.
    echo.
    echo  Install Python 3.8 or newer from:
    echo      https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: tick "Add python.exe to PATH" in the installer.
    echo  Then close this window, open a new one, and run run.bat again.
    echo.
    pause
    exit /b 1
)

REM ---- 2. Create the virtual environment (first run only) -----------
if not exist "%VENV_PY%" (
    echo  [1/3] Creating virtual environment...
    %BOOT_PY% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo.
        echo  [ERROR] Could not create the virtual environment.
        echo  Make sure Python is installed correctly and try again.
        echo.
        pause
        exit /b 1
    )
) else (
    echo  [1/3] Virtual environment ready.
)

REM ---- 3. Install dependencies (first run only) ---------------------
if not exist "%STAMP%" (
    echo  [2/3] Installing dependencies - first run only, please wait...
    REM Upgrading pip is a nicety, not a requirement - its result is ignored
    REM on purpose so a pip self-upgrade hiccup cannot block the install.
    "%VENV_PY%" -m pip install --upgrade pip --quiet
    "%VENV_PY%" -m pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo.
        echo  [ERROR] Installing dependencies failed.
        echo  Check your internet connection, then run run.bat again.
        echo.
        pause
        exit /b 1
    )
    echo installed > "%STAMP%"
) else (
    echo  [2/3] Dependencies ready.
)

REM ---- 4. Launch -----------------------------------------------------
echo  [3/3] Launching AriTyper...
echo.
echo  Keep this window open while you use the app.
echo  Close the AriTyper window to quit.
echo.

"%VENV_PY%" "%APP%"
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
    echo.
    echo  [AriTyper] Exited with code %RC%.
    echo  If that looks like an error, copy the message above when asking for help.
    echo.
    pause
)

endlocal & exit /b %RC%
