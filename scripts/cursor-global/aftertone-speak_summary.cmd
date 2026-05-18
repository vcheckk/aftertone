@echo off
REM Cursor hook: Python stdin (reliable on Windows). Optional curl if HOOK_JSON env set.
setlocal EnableExtensions
set "INSTALL=%USERPROFILE%\aftertone"
if exist "%USERPROFILE%\.cursor\hooks\aftertone-install-dir" (
  set /p INSTALL=<"%USERPROFILE%\.cursor\hooks\aftertone-install-dir"
)
set "PY=%INSTALL%\py\.venv\Scripts\python.exe"
set "ERR=%INSTALL%\.cursor\hooks\state\speak_summary-prepare.stderr.log"
set "LOG=%INSTALL%\.cursor\hooks\state\speak_summary-hook.log"
set "PORT=8765"
set "PORT_FILE=%INSTALL%\.cursor\hooks\state\tts-daemon.port"
if exist "%PORT_FILE%" set /p PORT=<"%PORT_FILE%"

if not exist "%PY%" (
  echo %DATE% %TIME% missing_venv %PY%>>"%LOG%"
  exit /b 0
)

set "AFTERTONE_REPO=%INSTALL%"
set "AFTERTONE_INSTALL_DIR=%INSTALL%"
set "PYTHONPATH=%INSTALL%\py"
cd /d "%INSTALL%\py"

REM Primary: stdin -> hook_run (Cursor pipes JSON here; curl @- often gets nothing under cmd /c).
"%PY%" -m aftertone.hook_run --stdin 2>>"%ERR%"
exit /b 0
