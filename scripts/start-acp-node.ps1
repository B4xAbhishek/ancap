#!/usr/bin/env pwsh
# Start the ACP node for the local ANCAP development stack.
#
# Usage:
#   .\scripts\start-acp-node.ps1            # starts in the foreground, logs to stdout
#   .\scripts\start-acp-node.ps1 -Background # background via helper script (env vars preserved)
#
# The node is required by:
#   - frontend-app /wallet/acp page (deposit address, balance, history)
#   - app/api/routers/wallet_acp.py (calls walletd against $ACP_RPC_URL)
#   - app/services/chain_anchor.py when CHAIN_ANCHOR_DRIVER=acp
# For *confirmed* on-chain tx in the app (blocks after genesis), use -EnableMiner so empty blocks
#   are mined; otherwise height stays at 1 and history shows only the genesis/coinbase.
#
# It listens on 0.0.0.0:8545 for local node operation.
# Public/default ACP RPC should now point to https://acp1.ancap.cloud/rpc.
#
# Creator vesting: default `cargo build --release` has NO on-chain vesting (see vesting.rs).
# Rebuilds run automatically if any `src\*.rs` (or `Cargo.toml`) is newer than `acp-node.exe`.
# -ForceBuild: always `cargo build --release`. -SkipBuild: never build (faster; risk stale EXE).
# -MainnetVestingBuild: build WITH `--features enforced-creator-vesting` (mainnet-style node).

[CmdletBinding()]
param(
    [switch]$Background,
    [string]$DataDir = (Join-Path $PSScriptRoot "..\Sicret\acp-node-data-host"),
    [string]$RpcListen = "0.0.0.0:8545",
    [int]$ChainId = 1001,
    [switch]$EnableMiner,
    [switch]$ForceBuild,
    [switch]$SkipBuild,
    [switch]$MainnetVestingBuild,
    [switch]$StrictCreatorVesting
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$crateDir = Join-Path $repoRoot "ACP-crypto\acp-node"
$nodeBin = Join-Path $crateDir "target\release\acp-node.exe"
$logFile = Join-Path $repoRoot "Sicret\acp-node.log"

$needsBuild = $false
if ($ForceBuild -or $MainnetVestingBuild) { $needsBuild = $true }
elseif (-not (Test-Path -LiteralPath $nodeBin)) { $needsBuild = $true }
elseif (-not $SkipBuild) {
    $srcRoot = Join-Path $crateDir "src"
    $man = @((Join-Path $crateDir "Cargo.toml"), (Join-Path $srcRoot "main.rs"), (Join-Path $srcRoot "vesting.rs"), (Join-Path $srcRoot "enforced_vesting.rs"))
    $stale = $false
    if (Test-Path -LiteralPath $nodeBin) {
        $exeT = (Get-Item -LiteralPath $nodeBin).LastWriteTimeUtc
        foreach ($p in $man) {
            if ((Test-Path -LiteralPath $p) -and ((Get-Item -LiteralPath $p).LastWriteTimeUtc -gt $exeT)) { $stale = $true; break }
        }
        if (-not $stale) {
            $allRs = Get-ChildItem -Path $srcRoot -Recurse -File -Filter "*.rs" -ErrorAction SilentlyContinue
            if ($allRs) {
                $newest = ($allRs | Measure-Object -Property LastWriteTimeUtc -Maximum).Maximum
                if ($newest -and $newest -gt $exeT) { $stale = $true }
            }
        }
    }
    if ($stale) { $needsBuild = $true }
}

if ($MainnetVestingBuild -and $SkipBuild) {
    throw "Cannot use -MainnetVestingBuild with -SkipBuild (a mainnet build is required)"
}
if ($needsBuild -and -not $SkipBuild) {
    Write-Host "Building acp-node (release)..." -ForegroundColor Cyan
    if ($MainnetVestingBuild) {
        Write-Host "  (with --features enforced-creator-vesting; for mainnet-style 69.3M rules, not default dev/bulk)" -ForegroundColor Yellow
    }
    Push-Location $crateDir
    try {
        if ($MainnetVestingBuild) {
            cargo build --release --features enforced-creator-vesting
        } else {
            cargo build --release
        }
    } finally {
        Pop-Location
    }
} elseif ($SkipBuild -and -not (Test-Path -LiteralPath $nodeBin)) {
    throw "acp-node binary missing and -SkipBuild set; run without -SkipBuild or: .\scripts\rebuild-acp-node.ps1"
}
if (-not (Test-Path -LiteralPath $nodeBin)) {
    throw "acp-node not found at $nodeBin. If the build said access denied, stop the running acp-node process, then re-run."
}

if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
}

$env:ACP_DATA_DIR = (Resolve-Path $DataDir).Path
$env:ACP_RPC_LISTEN = $RpcListen
$env:ACP_CHAIN_ID = "$ChainId"
$env:ACP_MINER_ENABLED = if ($EnableMiner) { "true" } else { "false" }

# Stacked controls (see vesting.rs): DISABLE wins; else ENFORCE=1 is required to apply 69.3M rules.
# Default dev: DISABLE=1 so both old and new acp-node binaries skip creator vesting (incl. background child).
# Use -StrictCreatorVesting for mainnet-style 69.3M vout0 (clears DISABLE, sets ENFORCE).
if ($StrictCreatorVesting) {
    $env:ACP_ENFORCE_CREATOR_VESTING = "1"
    Remove-Item Env:ACP_DISABLE_CREATOR_VESTING -ErrorAction SilentlyContinue
} else {
    Remove-Item Env:ACP_ENFORCE_CREATOR_VESTING -ErrorAction SilentlyContinue
    $env:ACP_DISABLE_CREATOR_VESTING = "1"
}

Write-Host "ACP node:" -ForegroundColor Cyan
Write-Host "  binary    : $nodeBin"
Write-Host "  data_dir  : $env:ACP_DATA_DIR"
Write-Host "  rpc       : $env:ACP_RPC_LISTEN"
Write-Host "  chain_id  : $env:ACP_CHAIN_ID"
Write-Host "  miner     : $env:ACP_MINER_ENABLED"
Write-Host "  vesting   : $( if ($env:ACP_ENFORCE_CREATOR_VESTING) { 'enforced (ENFORCE; use -StrictCreatorVesting)' } else { "skipped (ACP_DISABLE=$( $env:ACP_DISABLE_CREATOR_VESTING )); -Strict to enforce 69.3M" } )"

if ($Background) {
    Write-Host "Starting in background, logs -> $logFile" -ForegroundColor Cyan
    # Start-Process often drops session env on .NET; spawn a helper script so ACP_* (incl. vesting) is guaranteed.
    $dd = $env:ACP_DATA_DIR.Replace("'", "''")
    $rl = $env:ACP_RPC_LISTEN.Replace("'", "''")
    $ci = $env:ACP_CHAIN_ID.Replace("'", "''")
    $me = $env:ACP_MINER_ENABLED.Replace("'", "''")
    $nb = $nodeBin.Replace("'", "''")
    $lf = $logFile.Replace("'", "''")
    $lines = @(
        "`$env:ACP_DATA_DIR = '$dd'"
        "`$env:ACP_RPC_LISTEN = '$rl'"
        "`$env:ACP_CHAIN_ID = '$ci'"
        "`$env:ACP_MINER_ENABLED = '$me'"
    )
    if (-not [string]::IsNullOrWhiteSpace($env:ACP_PEER_RPC_URLS)) {
        $peer = $env:ACP_PEER_RPC_URLS.Replace("'", "''")
        $lines += "`$env:ACP_PEER_RPC_URLS = '$peer'"
    }
    if ($StrictCreatorVesting) {
        $lines += "`$env:ACP_ENFORCE_CREATOR_VESTING = '1'"
        $lines += "Remove-Item Env:ACP_DISABLE_CREATOR_VESTING -ErrorAction SilentlyContinue"
    } else {
        $lines += "Remove-Item Env:ACP_ENFORCE_CREATOR_VESTING -ErrorAction SilentlyContinue"
        $lines += "`$env:ACP_DISABLE_CREATOR_VESTING = '1'"
    }
    $lines += "& '$nb' *>&1 | Out-File -FilePath '$lf' -Encoding utf8"
    $runner = Join-Path $env:TEMP "acp-node-bg-$(New-Guid).ps1"
    Set-Content -Path $runner -Value ($lines -join "`n") -Encoding UTF8
    $psExe = "powershell.exe"
    if (Get-Command pwsh -ErrorAction SilentlyContinue) { $psExe = (Get-Command pwsh).Source }
    elseif (Get-Command pwsh.exe -ErrorAction SilentlyContinue) { $psExe = (Get-Command pwsh.exe).Source }
    $launched = $false
    try {
        Start-Process -FilePath $psExe -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $runner) -WindowStyle Hidden -ErrorAction Stop
        $launched = $true
    } catch {
        $winPs = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
        if (Test-Path -LiteralPath $winPs) {
            Start-Process -FilePath $winPs -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $runner) -WindowStyle Hidden
            $launched = $true
        }
    }
    if (-not $launched) { throw "Could not start background shell for acp-node (no pwsh/powershell in PATH). Run without -Background or add PowerShell 7+ to PATH." }
    Start-Sleep -Seconds 2
    if (Test-Path $logFile) { Get-Content -Path $logFile -Tail 15 }
}
else {
    Write-Host "Starting in foreground (Ctrl+C to stop)..." -ForegroundColor Cyan
    & $nodeBin
}
