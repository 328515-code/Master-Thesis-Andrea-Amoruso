@echo off
setlocal
cd /d "%~dp0"
rem Keep dependencies out of deeply nested thesis folders (Windows MAX_PATH).
set "EFV_ENV_DIR=%USERPROFILE%\.efv-tool\py313"
if not exist "%EFV_ENV_DIR%\Scripts\python.exe" (
  if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" -m venv "%EFV_ENV_DIR%"
  ) else (
    py -3.13 -m venv "%EFV_ENV_DIR%"
  )
  if errorlevel 1 goto fail
)
"%EFV_ENV_DIR%\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail
if /i "%~1"=="--setup-only" exit /b 0
"%EFV_ENV_DIR%\Scripts\python.exe" -m streamlit run streamlit_app.py
if errorlevel 1 goto fail
exit /b 0
:fail
echo Setup failed. Install Python 3.13 or consult README.md.
if /i "%~1"=="--setup-only" exit /b 1
pause
exit /b 1
