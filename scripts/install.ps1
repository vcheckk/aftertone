# One-line install (Windows): clone/update Aftertone, bootstrap, optional daemon start.
#
#   irm https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.ps1 | iex
#   # or with options:
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.ps1))) -InstallUv -StartDaemon
#
# Options:
#   -InstallDir PATH     Clone location (default: $env:USERPROFILE\aftertone)
#   -Branch NAME         Git branch (default: main)
#   -NoGlobal            Skip user-level Cursor hooks
#   -SkipAssets          Skip Hugging Face model download
#   -StartDaemon         Start tts_daemon after bootstrap
#   -InstallUv           Install uv via Astral if missing
#   -Help

param(
    [string] $InstallDir = $(if ($env:AFTERTONE_INSTALL_DIR) { $env:AFTERTONE_INSTALL_DIR } else { Join-Path $env:USERPROFILE "aftertone" }),
    [string] $Branch = $(if ($env:AFTERTONE_BRANCH) { $env:AFTERTONE_BRANCH } else { "main" }),
    [switch] $NoGlobal,
    [switch] $SkipAssets,
    [switch] $StartDaemon,
    [switch] $InstallUv,
    [switch] $Help
)

$ErrorActionPreference = "Stop"

$RepoUrl = if ($env:AFTERTONE_REPO_URL) { $env:AFTERTONE_REPO_URL } else { "https://github.com/omarelkhal/aftertone.git" }

function Show-Help {
    @"
Aftertone installer (Windows) — clone, bootstrap (uv + ONNX assets), optional daemon.

One-liner:
  irm https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.ps1 | iex

With options:
  & ([scriptblock]::Create((irm .../install.ps1))) -InstallUv -StartDaemon

Requires: git, Git for Windows (bash for Cursor hooks). Python 3.13 via uv (see py/.python-version).

Environment:
  AFTERTONE_INSTALL_DIR   Same as -InstallDir
  AFTERTONE_REPO_URL      Override git remote
  AFTERTONE_BRANCH        Same as -Branch
"@
}

if ($Help) { Show-Help; exit 0 }

function Ensure-Git {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Error "install: git is required. Install Git for Windows: https://git-scm.com/download/win"
    }
    $bash = @(
        "${env:ProgramFiles}\Git\bin\bash.exe",
        "${env:ProgramFiles(x86)}\Git\bin\bash.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $bash) {
        Write-Error "install: Git Bash not found (needed for Cursor hooks). Reinstall Git for Windows."
    }
}

function Ensure-Uv {
    $localBin = Join-Path $env:USERPROFILE ".local\bin"
    if (Test-Path $localBin) { $env:Path = "$localBin;$env:Path" }
    if (Get-Command uv -ErrorAction SilentlyContinue) { return }
    if ($InstallUv) {
        Write-Host "==> install: uv not found; running Astral installer…"
        irm https://astral.sh/uv/install.ps1 | iex
        $env:Path = "$localBin;$env:Path"
    }
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Write-Error "install: uv is required. Install: https://docs.astral.sh/uv/ or re-run with -InstallUv"
    }
}

function Clone-OrUpdate {
    $dir = $InstallDir
    $gitEa = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    if (Test-Path (Join-Path $dir ".git")) {
        Write-Host "==> install: updating $dir ($Branch)…"
        git -C $dir fetch origin $Branch --depth 1 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { git -C $dir fetch origin $Branch 2>&1 | Out-Null }
        git -C $dir checkout $Branch 2>&1 | Out-Null
        git -C $dir pull --ff-only origin $Branch 2>&1 | Out-Null
        $ErrorActionPreference = $gitEa
        if ($LASTEXITCODE -ne 0) {
            Write-Error "install: could not fast-forward; check $dir for local changes"
        }
    } else {
        Write-Host "==> install: cloning $RepoUrl → $dir ($Branch)…"
        $parent = Split-Path $dir -Parent
        if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
        git clone --depth 1 --branch $Branch $RepoUrl $dir 2>&1 | Out-Null
        $ErrorActionPreference = $gitEa
        if ($LASTEXITCODE -ne 0) {
            Write-Error "install: git clone failed"
        }
    }
    return (Resolve-Path $dir).Path
}

function Invoke-Bootstrap {
    param([string] $Root)
    Write-Host "==> install: bootstrap (uv sync + assets)…"
    $env:SKIP_WEB = "1"
    if ($SkipAssets) { $env:SKIP_ASSETS = "1" }
    & (Join-Path $Root "scripts\bootstrap.ps1")
}

function Install-GlobalHooks {
    param([string] $Root)
    Write-Host "==> install: user-level Cursor hooks ($env:USERPROFILE\.cursor)…"
    Push-Location (Join-Path $Root "py")
    $pyVer = $null
    $pvFile = Join-Path $Root "py\.python-version"
    if (Test-Path $pvFile) { $pyVer = (Get-Content $pvFile -Raw).Trim() }
    if ($pyVer) {
        uv run --python $pyVer python install_global_hooks.py --install-dir $Root
    } else {
        uv run python install_global_hooks.py --install-dir $Root
    }
    Pop-Location
}

function Start-TtsDaemon {
    param([string] $Root)
    Write-Host "==> install: starting tts_daemon…"
    Push-Location (Join-Path $Root "py")
    $pyVer = $null
    $pvFile = Join-Path $Root "py\.python-version"
    if (Test-Path $pvFile) { $pyVer = (Get-Content $pvFile -Raw).Trim() }
    try {
        if ($pyVer) {
            uv run --python $pyVer python tts_daemon_ctl.py start --repo-root ..
        } else {
            uv run python tts_daemon_ctl.py start --repo-root ..
        }
    } catch {
        Write-Warning "install: daemon start failed (run manually: cd $Root\py; uv run python tts_daemon_ctl.py start --repo-root ..)"
    }
    Pop-Location
}

function Show-NextSteps {
    param([string] $Root)
    $cursorHooks = Join-Path $env:USERPROFILE ".cursor\hooks.json"
    @"

==> Aftertone is ready at: $Root

Global install: spoken TTS hooks run in any Cursor project you open (if -NoGlobal was not used).
Config slash commands: open $Root in Cursor, or use /aftertone-* in Agent chat.

Next:
  1. Enable Hooks in Cursor Settings
  2. Trust each workspace where you want TTS
  3. Daemon: cd $Root\py; uv run python tts_daemon_ctl.py start --repo-root ..
  4. Turn on TTS: /aftertone-on in Agent chat

Hooks file: $cursorHooks
Docs: $Root\README.md
"@
}

Ensure-Git
$InstallDir = Clone-OrUpdate
Ensure-Uv
Invoke-Bootstrap -Root $InstallDir

if (-not $NoGlobal) {
    Install-GlobalHooks -Root $InstallDir
}

if ($StartDaemon) {
    Start-TtsDaemon -Root $InstallDir
}

Show-NextSteps -Root $InstallDir
