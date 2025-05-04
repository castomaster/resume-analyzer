@echo off
REM ───────────────────────────────────────────────────────────
REM  AI Resume Analyzer – one‑click launcher (Windows)
REM ───────────────────────────────────────────────────────────

:: 0) Перейти в каталог, где лежит .bat
cd /d "%~dp0"

:: 0.1) Определить, чем запускать Python → py или python
where py  >nul 2>nul
if %errorlevel%==0 (
  set "PY=py"
) else (
  set "PY=python"
)

:: ── 1. venv ────────────────────────────────────────────────
if not exist venv (
  echo [INFO] Creating virtual environment…
  %PY% -m venv venv  || goto :error
)

echo [INFO] Activating venv…
call venv\Scripts\activate.bat  || goto :error

:: ── 2. Dependencies ───────────────────────────────────────
echo [INFO] Upgrading pip…
%PY% -m pip install --upgrade pip  || goto :error

echo [INFO] Installing requirements…
%PY% -m pip install -r requirements.txt  || goto :error

:: ── 3. spaCy model (one‑time) ──────────────────────────────
echo [INFO] Checking spaCy model…
%PY% -m spacy validate | find /i "en_core_web_sm" >nul
if %errorlevel% neq 0 (
  echo [INFO] Downloading spaCy model…
  %PY% -m spacy download en_core_web_sm  || goto :error
)

:: ── 4. Launch Streamlit UI ─────────────────────────────────
echo [INFO] Launching Streamlit UI (http://localhost:8501) …
streamlit run App.py
goto :eof

:error
echo.
echo [ERROR] Something went wrong – see details above.
pause

