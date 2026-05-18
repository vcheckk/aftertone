# Repair Aftertone on Windows: global hooks only (no project hooks.json), daemon, TTS on.
# Run from any folder:
#   powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\aftertone\scripts\repair-windows-hooks.ps1"
# Or after clone:
#   powershell -ExecutionPolicy Bypass -File scripts\repair-windows-hooks.ps1

$ErrorActionPreference = "Stop"
$env:Path = "$env:USERPROFILE\.local\bin;C:\Program Files\Git\cmd;C:\Program Files\Git\bin;$env:Path"

$Install = if ($env:AFTERTONE_INSTALL_DIR) { $env:AFTERTONE_INSTALL_DIR } else { Join-Path $env:USERPROFILE "aftertone" }
if (-not (Test-Path (Join-Path $Install "py\speak_summary_prepare.py"))) {
    Write-Error "Aftertone not found at $Install. Run: irm https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.ps1 | iex"
}

# Remove project-level hooks that override / clash with global hooks
$here = (Get-Location).Path
$projHook = Join-Path $here ".cursor\hooks.json"
if (Test-Path $projHook) {
    Remove-Item $projHook -Force
    Write-Host "Removed project hooks.json at $projHook (use global hooks only)"
}

Write-Host "==> repair: global Cursor hooks..."
Push-Location (Join-Path $Install "py")
& uv run python install_global_hooks.py --install-dir $Install
Pop-Location

Write-Host "==> repair: enable TTS + spoken-summary rule..."
Push-Location (Join-Path $Install "py")
& uv run python speak_summary_toggle.py on
& uv run python sync_spoken_rule_lang.py
Pop-Location
$ruleSrc = Join-Path $Install ".cursor\rules\spoken-summary.mdc"
if (Test-Path $ruleSrc) {
    $rulesDir = Join-Path $env:USERPROFILE ".cursor\rules"
    New-Item -ItemType Directory -Path $rulesDir -Force | Out-Null
    Copy-Item $ruleSrc (Join-Path $rulesDir "spoken-summary.mdc") -Force
}

Write-Host "==> repair: start daemon..."
Push-Location (Join-Path $Install "py")
& uv run python tts_daemon_ctl.py start --repo-root ..
Pop-Location

$hooksJson = Join-Path $env:USERPROFILE ".cursor\hooks.json"
Write-Host ""
Write-Host "Done. Global hooks: $hooksJson"
Write-Host "After one Agent reply, check:"
Write-Host "  $env:USERPROFILE\.cursor\hooks\state\cursor-hook-fired.log  (Cursor ran the wrapper)"
Write-Host "  $Install\.cursor\hooks\state\speak_summary-hook.log       (prepare_ok / post_say_done)"
Write-Host "Reload Cursor. Settings -> Hooks ON. Trust workspace."
