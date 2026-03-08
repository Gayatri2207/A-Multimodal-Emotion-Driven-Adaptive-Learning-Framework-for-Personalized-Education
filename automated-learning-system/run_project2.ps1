# ========================================
# EMOTION-ADAPTIVE LEARNING SYSTEM
# Updated for Current Project Structure
# ========================================

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host $Message -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-WarnMsg {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Main {

    Write-Header "EMOTION-ADAPTIVE LEARNING SYSTEM"

    # Ensure Node path
    $env:PATH = "C:\Program Files\nodejs;$env:PATH"

    # ================================
    # BACKEND SETUP
    # ================================

    Write-Header "BACKEND SETUP"

    Set-Location "backend"

    if (-not (Test-Path ".venv")) {
        Write-Info "Creating backend virtual environment..."
        python -m venv .venv
        Write-Success "Virtual environment created."
    }
    else {
        Write-Success "Virtual environment exists."
    }

    Write-Info "Activating backend virtual environment..."
    .\.venv\Scripts\Activate.ps1
    Write-Success "Virtual environment activated."

    if (Test-Path "requirements.txt") {
        Write-Info "Installing backend dependencies..."
        pip install -r requirements.txt
        Write-Success "Backend dependencies installed."
    }
    else {
        Write-WarnMsg "requirements.txt not found in backend folder."
    }

    # Start backend
    Write-Info "Starting backend server..."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload"

    Set-Location ".."

    # ================================
    # FRONTEND SETUP
    # ================================

    Write-Header "FRONTEND SETUP"

    if (Test-Path "frontend_app\package.json") {

        Set-Location "frontend_app"

        Write-Info "Installing frontend dependencies..."
        npm install

        Write-Info "Starting frontend..."
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm start"

        Set-Location ".."
    }
    else {
        Write-WarnMsg "frontend_app not found."
    }

    Write-Success "System started successfully."
}

try {
    Main
}
catch {
    Write-Fail "Script error: $_"
}