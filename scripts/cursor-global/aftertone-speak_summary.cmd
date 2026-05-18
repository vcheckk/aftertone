@echo off
REM User-level Cursor hook (%USERPROFILE%\.cursor\hooks\). Delegates to Git Bash + speak_summary.sh.
setlocal EnableExtensions
set "ST=%USERPROFILE%\.cursor\hooks\state"
if not exist "%ST%" mkdir "%ST%"
echo %DATE% %TIME% cursor_fired>>"%ST%\cursor-hook-fired.log"

set "BASH=%ProgramFiles%\Git\bin\bash.exe"
if not exist "%BASH%" set "BASH=%ProgramFiles(x86)%\Git\bin\bash.exe"
if not exist "%BASH%" (
  echo %DATE% %TIME% no_git_bash>>"%ST%\cursor-hook-fired.log"
  exit /b 0
)

set "INSTALL=%USERPROFILE%\aftertone"
if exist "%USERPROFILE%\.cursor\hooks\aftertone-install-dir" (
  set /p INSTALL=<"%USERPROFILE%\.cursor\hooks\aftertone-install-dir"
)
set "TARGET=%INSTALL%\.cursor\hooks\speak_summary.sh"
if not exist "%TARGET%" (
  echo %DATE% %TIME% missing_target %TARGET%>>"%ST%\cursor-hook-fired.log"
  echo %DATE% %TIME% aftertone-speak_summary: missing %TARGET%>>"%INSTALL%\.cursor\hooks\state\speak_summary-hook.log" 2>nul
  exit /b 0
)
set "AFTERTONE_REPO=%INSTALL%"
set "AFTERTONE_INSTALL_DIR=%INSTALL%"
"%BASH%" "%TARGET%"
exit /b 0
