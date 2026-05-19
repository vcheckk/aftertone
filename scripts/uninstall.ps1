# Remove a global Aftertone install on Windows (Cursor hooks + optional install tree).
#
#   irm https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/uninstall.ps1 | iex
#   powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1 -InstallDir D:\aftertone -KeepDir
#
# Options:
#   -InstallDir PATH   Install root (default: marker file, then %USERPROFILE%\aftertone)
#   -KeepDir           Unregister Cursor hooks but keep the clone and assets
#   -NoGlobal          Skip %USERPROFILE%\.cursor cleanup (only stop daemon / remove -InstallDir)
#   -Yes               Skip confirmation before deleting the install directory
#   -DryRun            Print actions without changing anything
#   -Help

param(
    [string] $InstallDir = "",
    [switch] $KeepDir,
    [switch] $NoGlobal,
    [switch] $Yes,
    [switch] $DryRun,
    [switch] $Help
)

$ErrorActionPreference = "Stop"

$MarkerRel = "py\speak_summary_prepare.py"
$MarkerFile = Join-Path $env:USERPROFILE ".cursor\hooks\aftertone-install-dir"
$DefaultInstallDir = Join-Path $env:USERPROFILE "aftertone"

function Show-Help {
    @"
Aftertone uninstall (Windows) — stop daemon, remove user Cursor hooks, delete install tree.

One-liner:
  irm https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/uninstall.ps1 | iex

Keep the clone and ONNX assets (hooks only):
  irm .../uninstall.ps1 | iex -KeepDir

From an existing clone:
  powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1

Environment:
  AFTERTONE_INSTALL_DIR       Same as -InstallDir
  AFTERTONE_UNINSTALL_RAW_BASE  Override raw GitHub URL prefix for hook scripts when install tree is gone
"@
}

if ($Help) { Show-Help; exit 0 }

function Resolve-InstallDir {
    if ($env:AFTERTONE_INSTALL_DIR) {
        return [System.IO.Path]::GetFullPath($env:AFTERTONE_INSTALL_DIR)
    }
    if ($InstallDir) {
        return [System.IO.Path]::GetFullPath($InstallDir)
    }
    if (Test-Path -LiteralPath $MarkerFile) {
        $marked = (Get-Content -LiteralPath $MarkerFile -Raw).Trim()
        if ($marked) {
            return [System.IO.Path]::GetFullPath($marked)
        }
    }
    return [System.IO.Path]::GetFullPath($DefaultInstallDir)
}

function Test-IsAftertoneRoot {
    param([string] $Root)
    Test-Path -LiteralPath (Join-Path $Root $MarkerRel)
}

$script:ResolvedInstallDir = Resolve-InstallDir

function Stop-AftertoneDaemon {
    param([string] $Root)

    if (-not (Test-Path -LiteralPath (Join-Path $Root "py"))) { return }

    Write-Host "==> uninstall: stopping tts_daemon (if running)..."

    if ($DryRun) {
        Write-Host "would run: cd $Root\py && uv run python tts_daemon_ctl.py stop --repo-root .."
        return
    }

    $localBin = Join-Path $env:USERPROFILE ".local\bin"
    if (Test-Path $localBin) { $env:Path = "$localBin;$env:Path" }

    $pyDir = Join-Path $Root "py"
    $venvPy = Join-Path $pyDir ".venv\Scripts\python.exe"
    try {
        if (Test-Path -LiteralPath $venvPy) {
            Push-Location $pyDir
            try {
                & $venvPy tts_daemon_ctl.py stop --repo-root ".." 2>$null
            } finally {
                Pop-Location
            }
        } elseif (Get-Command uv -ErrorAction SilentlyContinue) {
            Push-Location $pyDir
            try {
                uv run python tts_daemon_ctl.py stop --repo-root ".." 2>$null
            } finally {
                Pop-Location
            }
        }
    } catch { }

    try {
        $conn = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($conn) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
            Write-Host "    stopped process on port 8765 (pid $($conn.OwningProcess))"
        }
    } catch { }

    Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*tts_daemon.py*" } |
        ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
}

function Invoke-UninstallGlobalHooks {
    param([string[]] $ExtraArgs)

    $scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { $null }
    $repoFromScript = if ($scriptRoot) {
        [System.IO.Path]::GetFullPath((Join-Path $scriptRoot ".."))
    } else { $null }

    $pyRoots = @()
    if ($repoFromScript -and (Test-Path -LiteralPath (Join-Path $repoFromScript "py\uninstall_global_hooks.py"))) {
        $pyRoots += $repoFromScript
    }
    if ($script:ResolvedInstallDir) {
        $installNorm = [System.IO.Path]::GetFullPath($script:ResolvedInstallDir)
        if ((Test-Path -LiteralPath (Join-Path $installNorm "py\uninstall_global_hooks.py")) -and
            ($null -eq $repoFromScript -or $installNorm -ne [System.IO.Path]::GetFullPath($repoFromScript))) {
            $pyRoots += $installNorm
        }
    }

    foreach ($root in $pyRoots) {
        $pyDir = Join-Path $root "py"
        $venvPy = Join-Path $pyDir ".venv\Scripts\python.exe"
        foreach ($runner in @(
                @{ Kind = "venv"; Exe = $venvPy },
                @{ Kind = "uv"; Exe = "uv" },
                @{ Kind = "python"; Exe = "python" }
            )) {
            if ($runner.Kind -eq "venv") {
                if (-not (Test-Path -LiteralPath $runner.Exe)) { continue }
            } elseif (-not (Get-Command $runner.Exe -ErrorAction SilentlyContinue)) {
                continue
            }
            Push-Location $pyDir
            try {
                if ($runner.Kind -eq "uv") {
                    $output = & $runner.Exe run python uninstall_global_hooks.py @ExtraArgs 2>&1
                } elseif ($runner.Kind -eq "venv") {
                    $output = & $runner.Exe uninstall_global_hooks.py @ExtraArgs 2>&1
                } else {
                    $output = & $runner.Exe uninstall_global_hooks.py @ExtraArgs 2>&1
                }
                if ($output) { $output | Write-Host }
                if ($?) {
                    return $true
                }
            } finally {
                Pop-Location
            }
        }
    }

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        return $false
    }

    $rawBase = if ($env:AFTERTONE_UNINSTALL_RAW_BASE) {
        $env:AFTERTONE_UNINSTALL_RAW_BASE
    } else {
        "https://raw.githubusercontent.com/omarelkhal/aftertone/main/py"
    }
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("aftertone-uninstall-" + [guid]::NewGuid().ToString("n"))
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    try {
        Write-Host "==> uninstall: fetching hook helpers from $rawBase ..."
        $installPy = Join-Path $tmp "install_global_hooks.py"
        $uninstallPy = Join-Path $tmp "uninstall_global_hooks.py"
        Invoke-WebRequest -Uri "$rawBase/install_global_hooks.py" -OutFile $installPy -UseBasicParsing
        Invoke-WebRequest -Uri "$rawBase/uninstall_global_hooks.py" -OutFile $uninstallPy -UseBasicParsing
        Push-Location $tmp
        try {
            $output = python uninstall_global_hooks.py @ExtraArgs 2>&1
            if ($output) { $output | Write-Host }
            return ($?)
        } finally {
            Pop-Location
        }
    } catch {
        Write-Error "uninstall: could not download uninstall_global_hooks.py (use a clone: powershell -File scripts\uninstall.ps1)"
        return $false
    } finally {
        Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Remove-GlobalHooks {
    Write-Host "==> uninstall: removing user-level Cursor hooks ($env:USERPROFILE\.cursor)..."
    $flags = @()
    if ($DryRun) { $flags += "--dry-run" }
    $ok = Invoke-UninstallGlobalHooks -ExtraArgs $flags
    if ($ok) { return }
    Write-Warning "uninstall: could not run uninstall_global_hooks.py (need python, uv, or an install tree)."
    Write-Warning "  Remove manually: $env:USERPROFILE\.cursor\hooks\aftertone-* and commands\aftertone-*"
}

function Remove-InstallDirectory {
    param([string] $Root)

    if ($KeepDir) {
        Write-Host "==> uninstall: keeping install directory (-KeepDir): $Root"
        return
    }

    if (-not (Test-IsAftertoneRoot -Root $Root)) {
        if (Test-Path -LiteralPath $Root) {
            Write-Warning "uninstall: $Root is not an Aftertone install (no $MarkerRel); not deleting."
        } else {
            Write-Host "==> uninstall: no install directory at $Root"
        }
        return
    }

    if ($DryRun) {
        Write-Host "would remove directory: $Root"
        return
    }

    if (-not $Yes) {
        Write-Host ""
        Write-Host "This will permanently delete:"
        Write-Host "  $Root"
        Write-Host '(including ONNX assets under assets/ - large download to restore.)'
        $confirm = Read-Host "Type yes to continue (type the word yes)"
        if ($confirm -ne "yes") {
            Write-Host "uninstall: cancelled (install directory kept)."
            return
        }
    }

    Write-Host "==> uninstall: removing $Root ..."
    if (-not (Test-Path -LiteralPath $Root)) { return }

    $retries = 3
    for ($i = 1; $i -le $retries; $i++) {
        try {
            Remove-Item -LiteralPath $Root -Recurse -Force -ErrorAction Stop
            Write-Host "removed: $Root"
            return
        } catch {
            if ($i -eq $retries) { throw }
            Write-Host "    retry $i/$retries (close Cursor terminals using the folder)..."
            Start-Sleep -Seconds 2
        }
    }
}

if (Test-IsAftertoneRoot -Root $script:ResolvedInstallDir) {
    Stop-AftertoneDaemon -Root $script:ResolvedInstallDir
}

if (-not $NoGlobal) {
    Remove-GlobalHooks
} else {
    Write-Host "==> uninstall: skipping $env:USERPROFILE\.cursor (-NoGlobal)"
}

Remove-InstallDirectory -Root $script:ResolvedInstallDir

Write-Host ""
Write-Host "==> Aftertone uninstall finished."
Write-Host ""
Write-Host "  Mute only (re-install hooks): irm .../install.ps1 | iex"
Write-Host '  Per-project speech hooks: remove afterAgentResponse from that repo .cursor\hooks.json'
Write-Host '  Docs: README.md - Uninstall'
