# End-to-end Windows uninstall verification (isolated fake profile + temp install).
# Does NOT touch the real %USERPROFILE%\.cursor or aftertone_v2.
$ErrorActionPreference = "Stop"

$repo = Split-Path $PSScriptRoot -Parent
$fakeHome = Join-Path $env:TEMP ("aftertone-uninstall-verify-" + [guid]::NewGuid().ToString("n"))
$fakeInstall = Join-Path $env:TEMP ("aftertone-uninstall-verify-install-" + [guid]::NewGuid().ToString("n"))

New-Item -ItemType Directory -Path (Join-Path $fakeInstall "py") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $fakeInstall "scripts\cursor-global") -Force | Out-Null
Set-Content -Path (Join-Path $fakeInstall "py\speak_summary_prepare.py") -Value "# stub"
Copy-Item -Path (Join-Path $repo "scripts\cursor-global\*") -Destination (Join-Path $fakeInstall "scripts\cursor-global") -Recurse -Force
New-Item -ItemType Directory -Path (Join-Path $fakeInstall ".cursor\commands") -Force | Out-Null
Set-Content -Path (Join-Path $fakeInstall ".cursor\commands\aftertone-on.md") -Value "# on"
New-Item -ItemType Directory -Path (Join-Path $fakeInstall ".cursor\rules") -Force | Out-Null
Set-Content -Path (Join-Path $fakeInstall ".cursor\rules\spoken-summary.mdc") -Value "# rule"

Write-Host "==> verify: fake HOME=$fakeHome"
Write-Host "==> verify: fake install=$fakeInstall"

# Install global hooks into fake profile (Python helper used by Linux/Windows uninstall too).
$installPy = @"
import os, sys
from pathlib import Path
sys.path.insert(0, r'$($repo -replace '\\','\\')\\py')
os.environ['USERPROFILE'] = r'$($fakeHome -replace '\\','\\')'
os.environ['HOME'] = os.environ['USERPROFILE']
from install_global_hooks import install_global
install_global(install_dir=Path(r'$($fakeInstall -replace '\\','\\')'))
"@

Push-Location (Join-Path $repo "py")
try {
    uv run python -c $installPy
    if ($LASTEXITCODE -ne 0) { throw "install_global failed" }
} finally {
    Pop-Location
}

$hookMarker = Join-Path $fakeHome ".cursor\hooks\aftertone-install-dir"
$hooksJson = Join-Path $fakeHome ".cursor\hooks.json"
if (-not (Test-Path $hookMarker)) { throw "FAIL: hook marker not created" }
if (-not (Test-Path $hooksJson)) { throw "FAIL: hooks.json not created" }
Write-Host "==> verify: hooks installed OK"

# Run uninstall.ps1 against fake profile + fake install (child process, isolated USERPROFILE).
$uninstallScript = Join-Path $PSScriptRoot "uninstall.ps1"
$childCmd = "set `"USERPROFILE=$fakeHome`"&& set `"HOME=$fakeHome`"&& powershell -NoProfile -ExecutionPolicy Bypass -File `"$uninstallScript`" -InstallDir `"$fakeInstall`" -Yes"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList @("/c", $childCmd) -Wait -PassThru -NoNewWindow
if ($p.ExitCode -ne 0) { throw "uninstall.ps1 exited $($p.ExitCode)" }

$checks = @(
    @{ Path = $hookMarker; Expect = $false; Label = "hook marker" },
    @{ Path = $hooksJson; Expect = $false; Label = "hooks.json" },
    @{ Path = (Join-Path $fakeHome ".cursor\commands\aftertone-on.md"); Expect = $false; Label = "slash command" },
    @{ Path = (Join-Path $fakeHome ".cursor\rules\spoken-summary.mdc"); Expect = $false; Label = "spoken rule" },
    @{ Path = $fakeInstall; Expect = $false; Label = "install directory" }
)
foreach ($c in $checks) {
    $exists = Test-Path -LiteralPath $c.Path
    if ($exists -ne $c.Expect) {
        throw "FAIL: $($c.Label) at $($c.Path) exists=$exists expected=$($c.Expect)"
    }
}

Write-Host "OK: Windows uninstall verified (hooks removed + install dir deleted)"
