<#
    AriTyper launcher for Windows (PowerShell)

    Usage, from a PowerShell prompt in this folder:

        .\run.ps1

    If PowerShell blocks the script, run it this way instead - this does
    not change any machine-wide setting:

        powershell -ExecutionPolicy Bypass -File .\run.ps1

    On first run this creates a private virtual environment and installs
    the dependencies. Later runs skip straight to launching the app.
#>

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

$VenvDir = '.venv'
$VenvPy  = Join-Path $VenvDir 'Scripts\python.exe'
$Stamp   = Join-Path $VenvDir '.deps-installed'
$App     = 'arityper_activated.py'

function Write-Step ($Message) { Write-Host "  $Message" -ForegroundColor Cyan }
function Write-Bad  ($Message) { Write-Host "  $Message" -ForegroundColor Red }

Write-Host ''
Write-Host '  ============================================' -ForegroundColor DarkCyan
Write-Host '    AriTyper - free, no license key needed'   -ForegroundColor DarkCyan
Write-Host '  ============================================' -ForegroundColor DarkCyan
Write-Host ''

# ---- 1. Find a Python interpreter to bootstrap with ---------------------
$BootPy = $null
foreach ($candidate in @(
        @{ Exe = 'py';     Args = @('-3') },
        @{ Exe = 'python'; Args = @()     })) {
    $cmd = Get-Command $candidate.Exe -ErrorAction SilentlyContinue
    if ($cmd) {
        # Confirm it actually runs - the Windows Store stub resolves but fails.
        & $candidate.Exe @($candidate.Args + '--version') *> $null
        if ($LASTEXITCODE -eq 0) { $BootPy = $candidate; break }
    }
}

if (-not $BootPy) {
    Write-Bad '[ERROR] Python was not found on this computer.'
    Write-Host ''
    Write-Host '  Install Python 3.8 or newer from:'
    Write-Host '      https://www.python.org/downloads/'
    Write-Host ''
    Write-Host '  IMPORTANT: tick "Add python.exe to PATH" in the installer,'
    Write-Host '  then open a new PowerShell window and run .\run.ps1 again.'
    Write-Host ''
    Read-Host '  Press Enter to close'
    exit 1
}

# ---- 2. Create the virtual environment (first run only) -----------------
if (-not (Test-Path -LiteralPath $VenvPy)) {
    Write-Step '[1/3] Creating virtual environment...'
    & $BootPy.Exe @($BootPy.Args + @('-m', 'venv', $VenvDir))
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $VenvPy)) {
        Write-Bad '[ERROR] Could not create the virtual environment.'
        Read-Host '  Press Enter to close'
        exit 1
    }
} else {
    Write-Step '[1/3] Virtual environment ready.'
}

# ---- 3. Install dependencies (first run only) ---------------------------
if (-not (Test-Path -LiteralPath $Stamp)) {
    Write-Step '[2/3] Installing dependencies - first run only, please wait...'
    # Upgrading pip is a nicety, not a requirement - its exit code is ignored
    # on purpose so a pip self-upgrade hiccup cannot block the install.
    & $VenvPy -m pip install --upgrade pip --quiet
    & $VenvPy -m pip install -r requirements.txt --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Bad '[ERROR] Installing dependencies failed.'
        Write-Host '  Check your internet connection, then run .\run.ps1 again.'
        Read-Host '  Press Enter to close'
        exit 1
    }
    Set-Content -LiteralPath $Stamp -Value 'installed'
} else {
    Write-Step '[2/3] Dependencies ready.'
}

# ---- 4. Launch -----------------------------------------------------------
Write-Step '[3/3] Launching AriTyper...'
Write-Host ''
Write-Host '  Keep this window open while you use the app.'
Write-Host '  Close the AriTyper window to quit.'
Write-Host ''

& $VenvPy $App
$rc = $LASTEXITCODE

if ($rc -ne 0) {
    Write-Host ''
    Write-Bad "[AriTyper] Exited with code $rc."
    Write-Host '  If that looks like an error, copy the message above when asking for help.'
    Read-Host '  Press Enter to close'
}

exit $rc
