@echo off
setlocal
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
  echo [1/4] Creating Python virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 goto :error
)

call .venv\Scripts\activate.bat
if errorlevel 1 goto :error

echo [2/4] Installing Python dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

if not exist .env (
  echo [3/4] Creating local .env from template...
  copy .env.example .env >nul
)

echo [4/4] Starting the web app at http://127.0.0.1:8000
python -m uvicorn app:app --reload
exit /b %errorlevel%

:error
echo Setup failed. Check that Python 3.11+ is installed and on PATH.
pause
exit /b 1
