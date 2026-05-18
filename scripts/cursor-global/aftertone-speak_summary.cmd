@echo off
REM User-level Cursor hook (~/.cursor/hooks/). Delegates to Git Bash + speak_summary.sh.
setlocal EnableExtensions
set "BASH=%ProgramFiles%\Git\bin\bash.exe"
if not exist "%BASH%" set "BASH=%ProgramFiles(x86)%\Git\bin\bash.exe"
if not exist "%BASH%" exit /b 0

set "INSTALL=%USERPROFILE%\aftertone"
if exist "%USERPROFILE%\.cursor\hooks\aftertone-install-dir" (
  set /p INSTALL=<"%USERPROFILE%\.cursor\hooks\aftertone-install-dir"
)
set "TARGET=%INSTALL%\.cursor\hooks\speak_summary.sh"
if not exist "%TARGET%" (
  if not exist "%USERPROFILE%\.cursor\hooks\state" mkdir "%USERPROFILE%\.cursor\hooks\state"
  echo %DATE% %TIME% aftertone-speak_summary: missing %TARGET%>>"%USERPROFILE%\.cursor\hooks\state\speak_summary-hook.log" 2>nul
  exit /b 0
)
set "AFTERTONE_REPO=%INSTALL%"
set "AFTERTONE_INSTALL_DIR=%INSTALL%"
"%BASH%" "%TARGET%"
exit /b 0
