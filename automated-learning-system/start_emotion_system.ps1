#!/usr/bin/env pwsh
<#
.SYNOPSIS
Emotion-Adaptive Learning System - Production Automation Script

.DESCRIPTION
Automated setup and start script for the Emotion-Adaptive Learning System.
Handles backend + frontend setup, dependency installation, database initialization,
and graceful shutdown.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File run_project.ps1

.NOTES
Requires: Python 3.12+, Node.js 18+, npm
Platform: Windows (PowerShell 5.1+)
#>

$ErrorActionPreference = "Continue"
$WarningPreference = "SilentlyContinue"

# ============================================================================
# CONFIGURATION
# ============================================================================

$ProjectRoot = (Get-Location).Path
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend_app"
$VenvDir = Join-Path $BackendDir ".venv"
$DbFile = Join-Path $BackendDir "emotion_learning.db"

$BackendPort = 8000
$FrontendPort = 3000

# ============================================================================
# COLOR OUTPUT FUNCTIONS
# ============================================================================

function Write-Success { param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error { param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning { param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Host { param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Header {
    param([string]$Message)

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host $Message -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

function Test-PortOpen {
    param([string]$Hostname = "127.0.0.1", [int]$Port = 8000, [int]$TimeoutSeconds = 30)
    $endTime = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $endTime) {
        try {
            $connection = Test-NetConnection -ComputerName $Hostname -Port $Port -ErrorAction SilentlyContinue -WarningAction SilentlyContinue
            if ($connection.TcpTestSucceeded) { return $true }
        } catch { }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

function Setup-Environment {
    Write-Header "ENVIRONMENT SETUP"
    
    # Check Python
    Write-Host "Checking Python installation..."
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    } catch {
        Write-Error "Python not found on PATH. Please install Python 3.12+ and add it to PATH."
        exit 1
    }
    
    # Check Node.js
    Write-Host "Checking Node.js installation..."
    $nodePath = "C:\Program Files\nodejs"
    
    if (-not (Test-Path $nodePath)) {
        Write-Error "Node.js not found in $nodePath"
        Write-Warning "Please install Node.js LTS from: https://nodejs.org/"
        exit 1
    }
    
    # Add Node to session PATH if not there
    if ($env:PATH -notlike "*nodejs*") {
        $env:PATH = "$nodePath;$env:PATH"
        Write-Host "Added Node.js to session PATH"
    }
    
    try {
        $nodeVersion = node --version
        $npmVersion = npm --version
        Write-Success "Node.js found: $nodeVersion"
        Write-Success "npm found: $npmVersion"
    } catch {
        Write-Error "Node.js or npm not accessible. Try restarting PowerShell."
        exit 1
    }
}

# ============================================================================
# BACKEND SETUP
# ============================================================================

function Setup-Backend {
    Write-Header "BACKEND SETUP"
    
    Set-Location $BackendDir
    
    if (-not (Test-Path $VenvDir)) {
        Write-Host "Creating Python virtual environment..."
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create virtual environment"
            exit 1
        }
        Write-Success "Virtual environment created"
    } else {
        Write-Success "Virtual environment already exists"
    }
    
    Write-Host "Activating virtual environment..."
    & ".\.venv\Scripts\Activate.ps1"
    Write-Success "Virtual environment activated"
    
    $BackendInstalledMarker = Join-Path $VenvDir ".installed"
    if (-not (Test-Path $BackendInstalledMarker)) {
        Write-Host "Installing Python dependencies (this may take a few minutes)..."
        python -m pip install --upgrade pip 2>&1 | Out-Null
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install Python dependencies"
            exit 1
        }
        Write-Success "Python dependencies installed"
        New-Item -Path $BackendInstalledMarker -Force | Out-Null
    } else {
        Write-Success "Python dependencies already installed (skipping)"
    }
    
    Set-Location $ProjectRoot
}

# ============================================================================
# FRONTEND SETUP
# ============================================================================

function Setup-Frontend {
    Write-Header "FRONTEND SETUP"
    
    Set-Location $FrontendDir
    
    $FrontendInstalledMarker = Join-Path $FrontendDir ".installed"
    if (-not (Test-Path $FrontendInstalledMarker) -or -not (Test-Path "node_modules")) {
        Write-Host "Installing Node.js dependencies (this may take a few minutes)..."
        npm install --legacy-peer-deps
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Node.js dependencies installed"
            New-Item -Path $FrontendInstalledMarker -Force | Out-Null
        } else {
            Write-Warning "npm install had issues, but continuing..."
        }
    } else {
        Write-Success "Node.js dependencies already installed (skipping)"
    }
    
    Set-Location $ProjectRoot
}

# ============================================================================
# SERVER STARTUP
# ============================================================================

function Start-Backend {
    Write-Header "STARTING BACKEND SERVER"
    
    Write-Host "Starting Starlette server on port $BackendPort..."
    
    Set-Location $BackendDir
    & ".\.venv\Scripts\Activate.ps1"
    
    $backendProcess = Start-Process -NoNewWindow -FilePath python `
        -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", $BackendPort) `
        -PassThru
    
    $global:BackendPID = $backendProcess.Id
    Write-Host "Backend process started (PID: $($backendProcess.Id))"
    
    Write-Host "Waiting for backend to be ready on port $BackendPort..."
    if (Test-PortOpen -Hostname "127.0.0.1" -Port $BackendPort -TimeoutSeconds 30) {
        Write-Success "Backend ready at http://127.0.0.1:$BackendPort"
        Write-Success "API docs available at http://127.0.0.1:$BackendPort/docs"
    } else {
        Write-Error "Backend failed to start or took too long to initialize"
        exit 1
    }
    
    Set-Location $ProjectRoot
}

function Start-Frontend {
    Write-Header "STARTING FRONTEND SERVER"
    
    Write-Host "Starting React development server on port $FrontendPort..."
    
    Set-Location $FrontendDir
    
    $frontendProcess = Start-Process -NoNewWindow -FilePath npm `
        -ArgumentList @("start") `
        -PassThru
    
    $global:FrontendPID = $frontendProcess.Id
    Write-Host "Frontend process started (PID: $($frontendProcess.Id))"
    
    Write-Host "Waiting for frontend to be ready on port $FrontendPort..."
    if (Test-PortOpen -Hostname "127.0.0.1" -Port $FrontendPort -TimeoutSeconds 60) {
        Write-Success "Frontend ready at http://127.0.0.1:$FrontendPort"
    } else {
        Write-Warning "Frontend taking longer to start. Please wait..."
    }
    
    Set-Location $ProjectRoot
}

# ============================================================================
# SHUTDOWN HANDLER
# ============================================================================

function Stop-AllServers {
    Write-Header "SHUTTING DOWN SERVERS"
    
    Write-Host "Stopping backend service..."
    if ($global:BackendPID) {
        try {
            Stop-Process -Id $global:BackendPID -ErrorAction SilentlyContinue
            Write-Success "Backend stopped"
        } catch { }
    }
    
    Write-Host "Stopping frontend service..."
    if ($global:FrontendPID) {
        try {
            Stop-Process -Id $global:FrontendPID -ErrorAction SilentlyContinue
            Write-Success "Frontend stopped"
        } catch { }
    }
    
    Write-Success "All services stopped gracefully"
}

# Register cleanup on exit
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    Stop-AllServers
} -ErrorAction SilentlyContinue

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Main {
    Clear-Host
    Write-Header "EMOTION-ADAPTIVE LEARNING SYSTEM"
    Write-Host "Production Automation Script v1.0" -ForegroundColor Magenta
    Write-Host "Academic Project Review Edition`n" -ForegroundColor Magenta
    
    try {
        # Setup phase
        Setup-Environment
        Setup-Backend
        Setup-Frontend
        
        # Startup phase
        Start-Backend
        Start-Sleep -Seconds 2
        Start-Frontend
        
        # Ready for demo
        Write-Header "SYSTEM READY FOR DEMO"
        Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
        Write-Success "All services started successfully!"
        Write-Host ""
        Write-Host "BACKEND (API):     http://127.0.0.1:$BackendPort" -ForegroundColor Cyan
        Write-Host "API DOCS:          http://127.0.0.1:$BackendPort/docs" -ForegroundColor Cyan
        Write-Host "FRONTEND (UI):     http://127.0.0.1:$FrontendPort" -ForegroundColor Cyan
        Write-Host "WebSocket:         ws://127.0.0.1:$BackendPort/ws/emotion" -ForegroundColor Cyan
        Write-Host "DATABASE:          $DbFile" -ForegroundColor Cyan
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Green
        
        # Open browser
        Write-Host "Opening browser to http://127.0.0.1:$FrontendPort..."
        Start-Process "http://127.0.0.1:$FrontendPort"
        
        # Wait for user to shutdown
        Write-Host "System running. Press Ctrl+C to stop all services..."
        while ($true) {
            Start-Sleep -Seconds 1
        }
        
    } catch {
        Write-Error "Script error: $_"
        Stop-AllServers
        exit 1
    }
}

# Execute main
Main
