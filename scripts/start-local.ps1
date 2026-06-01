param(
    [switch]$SkipInstall,
    [switch]$NoBrowser,
    [switch]$CheckOnly,
    [int]$BackendPort = 8765,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[LNE] $Message"
}

function Require-Command {
    param(
        [string]$Name,
        [string]$Hint
    )
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "$Name not found. $Hint"
    }
    return $cmd.Source
}

function Wait-LocalHttp {
    param(
        [string]$Url,
        [int]$Seconds = 45
    )
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3 | Out-Null
            return
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    throw "Timed out waiting for local service: $Url"
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Resolve-Path (Join-Path $ScriptDir "..")
$EngineDir = Join-Path $Root "engine"
$UiDir = Join-Path $EngineDir "ui"
$VenvDir = Join-Path $EngineDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$LogDir = Join-Path $Root ".local-run"

Write-Step "Project root: $Root"

$Python = Require-Command "python" "Install Python 3.10+ and make sure python is on PATH."
$Node = Require-Command "node" "Install Node.js 18+."
$Pnpm = Get-Command "pnpm" -ErrorAction SilentlyContinue
if (-not $Pnpm) {
    $Corepack = Get-Command "corepack" -ErrorAction SilentlyContinue
    if ($Corepack) {
        Write-Step "pnpm not found; trying corepack enable."
        & $Corepack.Source enable
        $Pnpm = Get-Command "pnpm" -ErrorAction SilentlyContinue
    }
}
if (-not $Pnpm) {
    throw "pnpm not found. Install pnpm, or run corepack enable and retry."
}
$PowerShellExe = (Get-Command "pwsh" -ErrorAction SilentlyContinue)
if (-not $PowerShellExe) {
    $PowerShellExe = Get-Command "powershell" -ErrorAction SilentlyContinue
}
if (-not $PowerShellExe) {
    throw "PowerShell runtime not found."
}

Write-Step "Python: $Python"
Write-Step "Node: $Node"
Write-Step "pnpm: $($Pnpm.Source)"

if ($CheckOnly) {
    Write-Step "Check complete; no dependencies installed and no services started."
    exit 0
}

if (-not $SkipInstall) {
    if (-not (Test-Path $VenvPython)) {
        Write-Step "Creating Python virtual environment."
        & $Python -m venv $VenvDir
    }
    Write-Step "Installing backend dependencies."
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -e $EngineDir

    Write-Step "Installing frontend dependencies."
    Push-Location $UiDir
    try {
        & $Pnpm.Source install
    } finally {
        Pop-Location
    }
} else {
    Write-Step "Dependency install skipped."
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$BackendUrl = "http://127.0.0.1:$BackendPort/api/settings/model-configuration"
$FrontendUrl = "http://127.0.0.1:$FrontendPort/"
$BackendLog = Join-Path $LogDir "backend.log"
$BackendErr = Join-Path $LogDir "backend.err.log"
$FrontendLog = Join-Path $LogDir "frontend.log"
$FrontendErr = Join-Path $LogDir "frontend.err.log"

$BackendCommand = "Set-Location -LiteralPath '$EngineDir'; & '$VenvPython' -m living_novel_engine.cli browse --host 127.0.0.1 --port $BackendPort --no-open"
$FrontendCommand = "Set-Location -LiteralPath '$UiDir'; pnpm run dev -- --host 127.0.0.1 --port $FrontendPort"

$Backend = $null
$Frontend = $null

try {
    Write-Step "Starting backend: http://127.0.0.1:$BackendPort/"
    $Backend = Start-Process -FilePath $PowerShellExe.Source -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $BackendCommand) -WindowStyle Hidden -PassThru -RedirectStandardOutput $BackendLog -RedirectStandardError $BackendErr

    Write-Step "Starting frontend: $FrontendUrl"
    $Frontend = Start-Process -FilePath $PowerShellExe.Source -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $FrontendCommand) -WindowStyle Hidden -PassThru -RedirectStandardOutput $FrontendLog -RedirectStandardError $FrontendErr

    Wait-LocalHttp -Url $BackendUrl
    Wait-LocalHttp -Url $FrontendUrl

    Write-Step "Local services are running."
    Write-Host "Frontend: $FrontendUrl"
    Write-Host "Backend: http://127.0.0.1:$BackendPort/"
    Write-Host "Logs: $LogDir"

    if (-not $NoBrowser) {
        Start-Process $FrontendUrl
    }

    Read-Host "Press Enter to stop local services"
} finally {
    foreach ($proc in @($Frontend, $Backend)) {
        if ($proc -and -not $proc.HasExited) {
            Stop-Process -Id $proc.Id -Force
        }
    }
    Write-Step "Local services stopped."
}
