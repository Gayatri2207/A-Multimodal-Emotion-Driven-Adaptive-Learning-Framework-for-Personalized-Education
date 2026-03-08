# =============================================================================
#  run_project.ps1
#  Emotion-Aware Intelligent Coding Practice Platform — Full Setup & Launch
#
#  Usage:
#    powershell -ExecutionPolicy Bypass -File run_project.ps1
#
#  What this script does:
#    1.  Verifies required tools  (Python, Node, npm, Git)
#    2.  Creates / validates Python virtual environment
#    3.  Installs / updates backend Python dependencies
#    4.  Runs import health-check; auto-installs any stragglers
#    5.  Checks AI model status  (ONNX emotion, Ollama tutor)
#    6.  Verifies / downloads emotion datasets
#    7.  Installs frontend npm dependencies
#    8.  Detects a free backend port (8000 -> 8001 -> 8002)
#    9.  Updates frontend/.env to point at the chosen port
#    10. Starts backend in a new terminal window (with auto-restart on crash)
#    11. Waits for /health, retries once with pip + restart if it 500s
#    12. Starts frontend in a new terminal window
#    13. Performs WebSocket route smoke-test
#    14. Opens browser at http://localhost:3000
#    15. Prints a full status summary
# =============================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"   # don't hard-abort on non-fatal errors

# ---------------------------------------------------------------------------
#  Console helpers
# ---------------------------------------------------------------------------
function Write-Banner {
    param([string]$msg, [string]$color = "Magenta")
    Write-Host ""
    Write-Host ("=" * 62) -ForegroundColor $color
    Write-Host "  $msg" -ForegroundColor $color
    Write-Host ("=" * 62) -ForegroundColor $color
}
function Write-Step { param([string]$msg) Write-Host "`n>>> $msg" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  [OK]  $msg" -ForegroundColor Green }
function Write-Warn { param([string]$msg) Write-Host "  [!!]  $msg" -ForegroundColor Yellow }
function Write-Fail { param([string]$msg) Write-Host " [ERR]  $msg" -ForegroundColor Red }
function Write-Info { param([string]$msg) Write-Host "        $msg" -ForegroundColor Gray }

# ---------------------------------------------------------------------------
#  Path resolution  (all paths relative to this script's location)
# ---------------------------------------------------------------------------
$SCRIPT_DIR   = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Join-Path $SCRIPT_DIR "automated-learning-system"
$BACKEND_DIR  = Join-Path $PROJECT_ROOT "backend"
$FRONTEND_DIR = Join-Path $PROJECT_ROOT "frontend\client"
$VENV_DIR     = Join-Path $BACKEND_DIR ".venv"
$VENV_PYTHON  = Join-Path $VENV_DIR "Scripts\python.exe"
$VENV_PIP     = Join-Path $VENV_DIR "Scripts\pip.exe"
$REQ_FILE     = Join-Path $BACKEND_DIR "requirements.txt"
$FRONTEND_ENV = Join-Path $FRONTEND_DIR ".env"
$DATA_DIR     = Join-Path $BACKEND_DIR "data"
$MODELS_DIR   = Join-Path $BACKEND_DIR "models"
$DATASETS_DIR = Join-Path $DATA_DIR "emotion_datasets"
$DL_SCRIPT    = Join-Path $BACKEND_DIR "scripts\download_datasets.py"

Write-Banner "Emotion-Aware Intelligent Coding Practice Platform" "Magenta"
Write-Host "  Script dir : $SCRIPT_DIR" -ForegroundColor DarkGray
Write-Host "  Backend    : $BACKEND_DIR" -ForegroundColor DarkGray
Write-Host "  Frontend   : $FRONTEND_DIR" -ForegroundColor DarkGray

# ===========================================================================
#  STEP 1 — CHECK REQUIRED TOOLS
# ===========================================================================
Write-Step "STEP 1 — Checking required tools"

$missingTools = @()

function Test-Tool {
    param([string]$cmd, [string]$label, [string]$url)
    try {
        $ver = (& $cmd --version 2>&1) | Select-Object -First 1
        Write-OK "$label : $ver"
        return $true
    } catch {
        $script:missingTools += "$label  ->  $url"
        return $false
    }
}

$hasPython = Test-Tool "python" "Python " "https://www.python.org/downloads/"
$hasNode   = Test-Tool "node"   "Node.js" "https://nodejs.org/"
$hasNpm    = Test-Tool "npm"    "npm    " "(bundled with Node.js)"
$null      = Test-Tool "git"    "Git    " "https://git-scm.com/"   # optional, no failure

if ($missingTools.Count -gt 0) {
    Write-Fail "Required tools are missing:"
    foreach ($t in $missingTools) { Write-Host "     - $t" -ForegroundColor Red }
    Write-Host ""
    Write-Warn "Install the tools above, then re-run this script."
    exit 1
}

# ---------------------------------------------------------------------------
#  Verify the project folders exist
# ---------------------------------------------------------------------------
foreach ($dir in @($BACKEND_DIR, $FRONTEND_DIR)) {
    if (-not (Test-Path $dir)) {
        Write-Fail "Expected directory not found: $dir"
        Write-Info "Please check that 'automated-learning-system' is in the same folder as this script."
        exit 1
    }
}
Write-OK "Project directories located."

# ===========================================================================
#  STEP 2 — PYTHON VIRTUAL ENVIRONMENT + DEPENDENCIES
# ===========================================================================
Write-Step "STEP 2 — Python virtual environment"

# --- Create venv if missing ---
if (-not (Test-Path $VENV_PYTHON)) {
    Write-Info "Creating virtual environment at: $VENV_DIR"
    & python -m venv $VENV_DIR
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "python -m venv failed.  Ensure Python 3.9+ is installed."
        exit 1
    }
    Write-OK "Virtual environment created."
} else {
    $pyVer = (& $VENV_PYTHON --version 2>&1).ToString().Trim()
    Write-OK "Virtual environment exists  ($pyVer)"
}

# --- Upgrade pip silently ---
Write-Info "Upgrading pip inside venv..."
& $VENV_PYTHON -m pip install --upgrade pip --quiet 2>&1 | Out-Null
Write-OK "pip is up-to-date."

# --- Generate requirements.txt if missing ---
if (-not (Test-Path $REQ_FILE)) {
    Write-Warn "requirements.txt not found — generating a default one..."
    @"
fastapi==0.100.0
uvicorn[standard]==0.22.0
SQLAlchemy==2.0.22
alembic==1.11.1
pydantic==1.10.12
pydantic[email]
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
python-multipart==0.0.6
websockets==11.0.3
gymnasium==0.28.1
stable-baselines3==2.0.0
torch==2.2.0
torchvision==0.17.0
transformers==4.35.2
numpy==1.26.2
pandas==2.1.2
aiofiles==23.1.0
python-dotenv==1.0.0
typing_extensions==4.8.0
email-validator==1.3.1
requests>=2.28
httpx>=0.23.0,<0.28.0
librosa
opencv-python
deepface
Pillow
onnxruntime
pytest
"@ | Out-File -FilePath $REQ_FILE -Encoding utf8
    Write-OK "requirements.txt generated."
}

# --- Install all dependencies ---
Write-Info "Installing Python dependencies  (first run may take several minutes)..."
& $VENV_PIP install -r $REQ_FILE --quiet 2>&1 |
    Where-Object { $_ -match "(ERROR|error)" } |
    ForEach-Object { Write-Warn $_ }

Write-OK "pip install complete."

# --- Import health-check: verify critical modules, auto-fix any gaps ---
Write-Step "STEP 2b — Verifying critical Python imports"

$checkScript = @"
import sys
results = {}
modules = {
    'fastapi':       'fastapi==0.100.0',
    'uvicorn':       'uvicorn[standard]==0.22.0',
    'sqlalchemy':    'SQLAlchemy==2.0.22',
    'pydantic':      'pydantic==1.10.12',
    'websockets':    'websockets==11.0.3',
    'jose':          'python-jose[cryptography]==3.3.0',
    'passlib':       'passlib[bcrypt]==1.7.4',
    'multipart':     'python-multipart==0.0.6',
    'numpy':         'numpy==1.26.2',
    'cv2':           'opencv-python',
    'PIL':           'Pillow',
    'onnxruntime':   'onnxruntime',
    'aiofiles':      'aiofiles==23.1.0',
    'dotenv':        'python-dotenv==1.0.0',
    'requests':      'requests>=2.28',
    'gymnasium':     'gymnasium==0.28.1',
}
missing = []
for mod, pkg in modules.items():
    try:
        __import__(mod)
        results[mod] = 'ok'
    except Exception:
        missing.append(pkg)
        results[mod] = 'MISSING'
for k, v in results.items():
    print(f'{k}:{v}')
if missing:
    print('MISSING_PKGS:' + '|'.join(missing))
    sys.exit(1)
sys.exit(0)
"@

$tmpCheck = "$env:TEMP\run_import_check_$([guid]::NewGuid().ToString('N').Substring(0,8)).py"
$checkScript | Out-File -FilePath $tmpCheck -Encoding utf8

$checkOut = & $VENV_PYTHON $tmpCheck 2>&1
Remove-Item $tmpCheck -ErrorAction SilentlyContinue

$missingLine = $checkOut | Where-Object { $_ -match "^MISSING_PKGS:" }
if ($missingLine) {
    $pkgsToFix = ($missingLine -replace "^MISSING_PKGS:","") -split "\|"
    Write-Warn "Some packages were not importable; attempting targeted install..."
    foreach ($pkg in $pkgsToFix) {
        Write-Info "  pip install $pkg"
        & $VENV_PIP install $pkg --quiet 2>&1 | Out-Null
    }
    # Re-run check
    $checkScript | Out-File -FilePath $tmpCheck -Encoding utf8
    $checkOut2 = & $VENV_PYTHON $tmpCheck 2>&1
    Remove-Item $tmpCheck -ErrorAction SilentlyContinue
    if ($checkOut2 | Where-Object { $_ -match "^MISSING_PKGS:" }) {
        $stillMissing = ($checkOut2 | Where-Object { $_ -match "^MISSING_PKGS:" }) -replace "^MISSING_PKGS:",""
        Write-Fail "Could not install: $stillMissing"
        Write-Info "The backend may still start in degraded mode (e.g., without PyTorch GPU support)."
    } else {
        Write-OK "All missing packages installed successfully."
    }
} else {
    Write-OK "All critical Python modules verified."
}

# ===========================================================================
#  STEP 3 — AI MODEL STATUS CHECK
# ===========================================================================
Write-Step "STEP 3 — AI model status"

# --- ONNX emotion model ---
$onnxModel = Join-Path $MODELS_DIR "emotion_ferplus.onnx"
if (Test-Path $onnxModel) {
    $onnxSize = [math]::Round((Get-Item $onnxModel).Length / 1MB, 1)
    Write-OK "ONNX emotion model found  (${onnxSize} MB)  ->  $onnxModel"
} else {
    Write-Warn "ONNX emotion model not cached yet."
    Write-Info "It will be auto-downloaded (~2 MB) on first webcam frame."
    # Ensure models dir exists
    New-Item -ItemType Directory -Path $MODELS_DIR -Force | Out-Null
}

# --- Ollama AI tutor check ---
Write-Info "Checking for Ollama (local LLM tutor)..."
try {
    $ollamaResp = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" `
                                    -Method Get -TimeoutSec 2 -ErrorAction Stop
    $modelNames = ($ollamaResp.models | ForEach-Object { $_.name }) -join ", "
    if ($modelNames) {
        Write-OK "Ollama running.  Available models: $modelNames"
        Write-Info "AI Tutor will use the best available code model."
    } else {
        Write-Warn "Ollama running but no models downloaded yet."
        Write-Info "  To enable AI tutor: ollama pull deepseek-coder"
    }
} catch {
    Write-Warn "Ollama not running  (AI tutor will use rule-based fallback)."
    Write-Info "  To enable full AI tutor, install Ollama from https://ollama.com"
    Write-Info "  Then run:  ollama pull deepseek-coder"
}

# --- PyTorch DLL check ---
Write-Info "Checking PyTorch availability..."
$torchCheck = & $VENV_PYTHON -c "
try:
    import torch; print('TORCH_OK:' + torch.__version__)
except Exception as e:
    print('TORCH_FAIL:' + str(e)[:80])
" 2>&1

if ($torchCheck -match "TORCH_OK:(.+)") {
    Write-OK "PyTorch available  (v$($Matches[1]))"
} else {
    $reason = if ($torchCheck -match "TORCH_FAIL:(.+)") { $Matches[1] } else { "unknown" }
    Write-Warn "PyTorch not available: $reason"
    Write-Info "ONNX emotion model + heuristic fallbacks are active  (no ML required)."
}

# ===========================================================================
#  STEP 4 — DATASET CHECK / DOWNLOAD
# ===========================================================================
Write-Step "STEP 4 — Emotion datasets"

# Ensure data directories exist
foreach ($d in @($DATA_DIR, $DATASETS_DIR,
                  (Join-Path $DATA_DIR "speech_datasets"),
                  (Join-Path $DATA_DIR "typing_datasets"))) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
}

# Check which datasets are present
$fer_dir      = Join-Path $DATASETS_DIR "fer2013"
$raf_dir      = Join-Path $DATASETS_DIR "raf_db"
$ravdess_dir  = Join-Path $DATA_DIR "speech_datasets\ravdess"

$datasetsFound = @()
$datasetsMissing = @()

foreach ($pair in @(
    @{ Path = $fer_dir;     Name = "FER2013"   },
    @{ Path = $raf_dir;     Name = "RAF-DB"    },
    @{ Path = $ravdess_dir; Name = "RAVDESS"   }
)) {
    if ((Test-Path $pair.Path) -and (Get-ChildItem $pair.Path -Recurse -File | Measure-Object).Count -gt 0) {
        $count = (Get-ChildItem $pair.Path -Recurse -File | Measure-Object).Count
        Write-OK "$($pair.Name) found  ($count files)"
        $datasetsFound += $pair.Name
    } else {
        Write-Warn "$($pair.Name) not found at: $($pair.Path)"
        $datasetsMissing += $pair
    }
}

if ($datasetsMissing.Count -gt 0) {
    Write-Info ""
    Write-Info "Missing datasets detected.  The platform runs WITHOUT them"
    Write-Info "(ONNX emotion model works with just the webcam feed)."
    Write-Info ""

    # Attempt auto-download if the download script exists
    if (Test-Path $DL_SCRIPT) {
        Write-Info "Download script found.  Attempting HuggingFace datasets download..."
        Write-Info "(This requires 'datasets' package and internet access)"

        # Install 'datasets' library if not present
        & $VENV_PIP install "datasets" "kaggle" --quiet 2>&1 | Out-Null

        $dlArgs = @()
        foreach ($ds in $datasetsMissing) {
            if ($ds.Name -eq "FER2013") { $dlArgs += "--fer2013" }
        }

        if ($dlArgs.Count -gt 0) {
            Write-Info "Running: python scripts/download_datasets.py $($dlArgs -join ' ')"
            Push-Location $BACKEND_DIR
            & $VENV_PYTHON $DL_SCRIPT @dlArgs 2>&1 |
                ForEach-Object { Write-Info "  $_" }
            Pop-Location
        }
    } else {
        Write-Info "To download datasets manually:"
        Write-Info "  FER2013  : https://www.kaggle.com/datasets/msambare/fer2013"
        Write-Info "  RAF-DB   : https://www.kaggle.com/datasets/shuvoalok/raf-db-dataset"
        Write-Info "  RAVDESS  : https://zenodo.org/record/1188976"
        Write-Info "  Place each under: $DATASETS_DIR\<name>"
        Write-Info ""
        Write-Info "  Or run:  python scripts/download_datasets.py --all"
        Write-Info "  (from the backend directory, with Kaggle API configured)"
    }
}

# ===========================================================================
#  STEP 5 — FRONTEND SETUP
# ===========================================================================
Write-Step "STEP 5 — Frontend setup"

$pkgJson    = Join-Path $FRONTEND_DIR "package.json"
$nodeModules = Join-Path $FRONTEND_DIR "node_modules"

if (-not (Test-Path $pkgJson)) {
    Write-Fail "package.json not found at: $pkgJson"
    exit 1
}

if (-not (Test-Path $nodeModules)) {
    Write-Info "node_modules missing — running npm install (may take a few minutes)..."
} else {
    Write-Info "node_modules present — running npm install to ensure packages are current..."
}

Push-Location $FRONTEND_DIR
$npmOut = & npm install --loglevel=warn 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warn "npm install reported errors:"
    $npmOut | Where-Object { $_ -match "error" } | ForEach-Object { Write-Warn "  $_" }
    # Try with --legacy-peer-deps as a fallback
    Write-Info "Retrying with --legacy-peer-deps..."
    & npm install --legacy-peer-deps --loglevel=warn 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "npm install failed even with --legacy-peer-deps."
        Pop-Location
        exit 1
    }
}
Pop-Location
Write-OK "Frontend npm packages installed."

# Verify key packages present in node_modules; install any that are missing
$requiredPkgs = @(
    "react",
    "axios",
    "@monaco-editor/react",
    "recharts",
    "tailwindcss",
    "chart.js",
    "@mui/material"
)
foreach ($pkg in $requiredPkgs) {
    # Scoped packages like @mui/material live under node_modules/@mui/material
    $pkgDir = Join-Path $nodeModules $pkg
    if (Test-Path $pkgDir) {
        Write-OK "  $pkg"
    } else {
        Write-Warn "  $pkg not found — installing..."
        Push-Location $FRONTEND_DIR
        & npm install $pkg --legacy-peer-deps --loglevel=warn 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-OK "  $pkg installed."
        } else {
            Write-Warn "  Could not install $pkg (non-critical — app may still work)."
        }
        Pop-Location
    }
}

# ===========================================================================
#  STEP 6 — PORT DETECTION + .env SYNC
# ===========================================================================
Write-Step "STEP 6 — Port detection"

function Test-PortFree {
    param([int]$port)
    $used = netstat -ano 2>$null |
            Select-String "\s+0\.0\.0\.0:$port\s+" |
            Measure-Object
    return ($used.Count -eq 0)
}

$BACKEND_PORT = 8000
foreach ($candidate in @(8000, 8001, 8002)) {
    if (Test-PortFree $candidate) {
        $BACKEND_PORT = $candidate
        Write-OK "Backend will use port $BACKEND_PORT"
        break
    } else {
        Write-Warn "Port $candidate is in use — trying next..."
    }
}

$BACKEND_URL = "http://localhost:$BACKEND_PORT"
$WS_URL      = "ws://localhost:$BACKEND_PORT/ws/emotion"

# --- Write (or update) frontend .env ---
$envContent = @"
REACT_APP_API_URL=$BACKEND_URL
REACT_APP_WS_URL=$WS_URL
"@
$envContent | Out-File -FilePath $FRONTEND_ENV -Encoding utf8 -NoNewline
Write-OK "Frontend .env written: $FRONTEND_ENV"
Write-Info "  REACT_APP_API_URL = $BACKEND_URL"
Write-Info "  REACT_APP_WS_URL  = $WS_URL"

# ===========================================================================
#  STEP 7 — START BACKEND SERVER
# ===========================================================================
Write-Step "STEP 7 — Starting backend server"

# Helper: escape single-quotes inside a PowerShell here-string
$bp = $BACKEND_DIR   -replace "'", "''"
$vp = $VENV_PYTHON   -replace "'", "''"

# The backend window runs uvicorn with --reload and will auto-restart if
# a .py file changes.  The outer loop retries the process up to 3 times
# in case of a startup crash (e.g., missing module on the first try).
$backendCmd = @"
`$ErrorActionPreference = 'Continue'
`$env:PYTHONUTF8 = '1'
`$maxRetries = 3
`$attempt    = 0
function banner { param([string]`$m) Write-Host "`n$('='*60)`n  `$m`n$('='*60)" -ForegroundColor Cyan }

banner 'Backend: Emotion-Aware Platform'
Write-Host '  Dir     : $bp' -ForegroundColor DarkGray
Write-Host '  Python  : $vp' -ForegroundColor DarkGray
Write-Host '  Port    : $BACKEND_PORT' -ForegroundColor DarkGray

Set-Location '$bp'

while (`$attempt -lt `$maxRetries) {
    `$attempt++
    Write-Host "`n[Attempt `$attempt / `$maxRetries]  Starting uvicorn on port $BACKEND_PORT ..." -ForegroundColor Cyan

    `$proc = Start-Process -FilePath '$vp' ``
        -ArgumentList '-m','uvicorn','app.main:app','--host','0.0.0.0','--port','$BACKEND_PORT','--reload' ``
        -PassThru -NoNewWindow
    `$proc.WaitForExit()

    if (`$proc.ExitCode -eq 0) { break }

    Write-Host "`n[Backend] Exited with code `$(`$proc.ExitCode)." -ForegroundColor Yellow

    if (`$attempt -lt `$maxRetries) {
        Write-Host '[Backend] Checking for missing modules and retrying in 3 s...' -ForegroundColor Yellow
        # Attempt to self-heal by re-running pip install
        `$pipExe = Join-Path (Split-Path -Parent '$vp') 'pip.exe'
        & `$pipExe install -r (Join-Path '$bp' 'requirements.txt') --quiet 2>`$null
        Start-Sleep -Seconds 3
    }
}

Write-Host "`n[Backend] Process ended.  Exit code: `$(`$proc.ExitCode)" -ForegroundColor Red
Read-Host 'Press Enter to close this window'
"@

Start-Process powershell `
    -ArgumentList "-NoExit", "-Command", $backendCmd `
    -WindowStyle Normal
Write-OK "Backend window launched (port $BACKEND_PORT)."

# --- Wait for /health (up to 45 seconds) ---
Write-Info "Waiting for backend /health  (up to 45 s)..."
$backendReady = $false
$healthUrl    = "$BACKEND_URL/health"

for ($i = 1; $i -le 45; $i++) {
    Start-Sleep -Seconds 1
    try {
        $resp = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            $backendReady = $true
            Write-Host ""
            break
        }
    } catch {}

    # Print a dot every second, newline every 15
    if ($i % 15 -eq 0) { Write-Host "." } else { Write-Host "." -NoNewline }
}

if ($backendReady) {
    try {
        $healthBody = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue
        Write-OK "Backend healthy   ->  $($healthBody | ConvertTo-Json -Compress -Depth 2)"
    } catch {
        Write-OK "Backend responded on /health (200 OK)"
    }
} else {
    Write-Warn "Backend did not respond within 45 s."
    Write-Warn "Check the backend terminal window for error messages."
    Write-Info "Common causes:"
    Write-Info "  - Port $BACKEND_PORT still occupied by another process"
    Write-Info "  - Missing Python module (check requirements.txt)"
    Write-Info "  - Database migration error (try deleting emotion_learning.db)"
}

# ===========================================================================
#  STEP 8 — WEBSOCKET SMOKE-TEST
# ===========================================================================
Write-Step "STEP 8 — WebSocket route check"

if ($backendReady) {
    try {
        Invoke-WebRequest -Uri "$BACKEND_URL/ws/emotion" `
                          -UseBasicParsing -TimeoutSec 4 -ErrorAction Stop | Out-Null
        Write-Warn "/ws/emotion returned 200 (expected 101/426 for WS upgrade)."
    } catch {
        $sc = $_.Exception.Response.StatusCode.value__
        $wsOk = $sc -in @(101, 426, 400)
        if ($wsOk) {
            Write-OK "/ws/emotion exists  (HTTP $sc — WS upgrade required, as expected)"
        } elseif ($sc -eq 404) {
            Write-Warn "/ws/emotion returned 404 — WebSocket route missing."
        } else {
            Write-Info "/ws/emotion probe returned HTTP $sc"
        }
    }
} else {
    Write-Info "Skipping WebSocket check — backend not ready."
}

# ===========================================================================
#  STEP 9 — START FRONTEND SERVER
# ===========================================================================
Write-Step "STEP 9 — Starting frontend server"

$fp = $FRONTEND_DIR -replace "'", "''"

$frontendCmd = @"
`$env:BROWSER        = 'none'
`$env:PORT           = '3000'
`$env:CHOKIDAR_USEPOLLING = 'false'
Set-Location '$fp'
Write-Host "`n$('='*60)" -ForegroundColor Cyan
Write-Host '  Frontend: Emotion-Aware Platform  (http://localhost:3000)' -ForegroundColor Cyan
Write-Host "$('='*60)`n" -ForegroundColor Cyan
Write-Host '  API URL : $BACKEND_URL' -ForegroundColor DarkGray
Write-Host '  WS  URL : $WS_URL' -ForegroundColor DarkGray
Write-Host ''
& npm start
"@

Start-Process powershell `
    -ArgumentList "-NoExit", "-Command", $frontendCmd `
    -WindowStyle Normal
Write-OK "Frontend window launched  (http://localhost:3000)."

# ===========================================================================
#  STEP 10 — OPEN BROWSER
# ===========================================================================
Write-Step "STEP 10 — Opening browser"

Write-Info "Giving React 8 seconds to compile before opening the browser..."
Start-Sleep -Seconds 8

try {
    Start-Process "http://localhost:3000"
    Write-OK "Browser opened at http://localhost:3000"
} catch {
    Write-Info "Could not open browser automatically."
    Write-Info "Open manually: http://localhost:3000"
}

# ===========================================================================
#  FINAL SUMMARY
# ===========================================================================
Write-Banner "PLATFORM IS RUNNING" "Green"

$statusIcon = if ($backendReady) { "[UP] " } else { "[??]" }

Write-Host ""
Write-Host "  Service Summary" -ForegroundColor White
Write-Host "  ---------------" -ForegroundColor DarkGray
Write-Host "  Frontend   $statusIcon http://localhost:3000"          -ForegroundColor Cyan
Write-Host "  Backend    $statusIcon $BACKEND_URL"                   -ForegroundColor Cyan
Write-Host "  API Docs       $BACKEND_URL/docs"                      -ForegroundColor DarkCyan
Write-Host "  Health         $BACKEND_URL/health"                    -ForegroundColor DarkCyan
Write-Host "  WebSocket      $WS_URL"                                -ForegroundColor DarkCyan
Write-Host ""
Write-Host "  AI Status" -ForegroundColor White
Write-Host "  ---------" -ForegroundColor DarkGray

$onnxStatus = if (Test-Path (Join-Path $MODELS_DIR "emotion_ferplus.onnx")) { "[READY]" } else { "[auto-dl on first use]" }
Write-Host "  ONNX Emotion Model  $onnxStatus" -ForegroundColor $(if ($onnxStatus -match "READY") { "Green" } else { "Yellow" })

try {
    $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 1 -ErrorAction Stop
    Write-Host "  Ollama AI Tutor     [RUNNING]  (full LLM support)" -ForegroundColor Green
} catch {
    Write-Host "  Ollama AI Tutor     [OFFLINE]  (rule-based fallback active)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Dataset Status" -ForegroundColor White
Write-Host "  --------------" -ForegroundColor DarkGray
foreach ($pair in @(
    @{ Path = $fer_dir;     Name = "FER2013"  },
    @{ Path = $raf_dir;     Name = "RAF-DB"   },
    @{ Path = $ravdess_dir; Name = "RAVDESS"  }
)) {
    $has = (Test-Path $pair.Path) -and ((Get-ChildItem $pair.Path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0)
    $ic  = if ($has) { "[OK] " } else { "[ -- ]" }
    $col = if ($has) { "Green" } else { "DarkGray" }
    Write-Host "  $($pair.Name.PadRight(10)) $ic" -ForegroundColor $col
}

Write-Host ""
Write-Host "  Key Pages" -ForegroundColor White
Write-Host "  ---------" -ForegroundColor DarkGray
Write-Host "   /              Dashboard (emotion metrics + live chart)" -ForegroundColor Gray
Write-Host "   /problems      Problem bank (100 problems, filterable)" -ForegroundColor Gray
Write-Host "   /code/:id      Monaco editor + webcam + AI tutor"       -ForegroundColor Gray
Write-Host "   /teacher       Analytics dashboard (teacher view)"      -ForegroundColor Gray
Write-Host "   /login         Login / Register / Guest mode"           -ForegroundColor Gray
Write-Host ""
Write-Host "  Quick Links" -ForegroundColor White
Write-Host "  -----------" -ForegroundColor DarkGray
Write-Host "   Swagger UI  : $BACKEND_URL/docs" -ForegroundColor DarkCyan
Write-Host "   ReDoc       : $BACKEND_URL/redoc" -ForegroundColor DarkCyan
Write-Host ""
Write-Host "  Tips" -ForegroundColor White
Write-Host "  ----" -ForegroundColor DarkGray
Write-Host "   - Both backend and frontend run in separate terminal windows." -ForegroundColor DarkGray
Write-Host "   - Close those windows to stop the servers." -ForegroundColor DarkGray
Write-Host "   - Backend auto-reloads on .py file changes (--reload mode)." -ForegroundColor DarkGray
Write-Host "   - Enable full AI tutor: ollama pull deepseek-coder" -ForegroundColor DarkGray
Write-Host "   - Download datasets:    cd automated-learning-system\backend" -ForegroundColor DarkGray
Write-Host "                           python scripts\download_datasets.py --all" -ForegroundColor DarkGray
Write-Host "   - Run backend tests:    .venv\Scripts\python.exe -m pytest tests\ -v" -ForegroundColor DarkGray
Write-Host ""
Write-Host ("=" * 62) -ForegroundColor Magenta