$ErrorActionPreference = "Stop"

function Write-OK { param($msg) Write-Host "[ OK ] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err { param($msg) Write-Host "[ERR ] $msg" -ForegroundColor Red }

try {
    Write-Host "Starting automated run_project.ps1" -ForegroundColor Cyan

    # Determine script root
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    Set-Location $scriptDir

    # Paths
    $backendPath = Join-Path $scriptDir "backend"
    $frontendPath = Join-Path $scriptDir "frontend_app"
    $venvPath = Join-Path $backendPath ".venv"
    $venvPython = Join-Path $venvPath "Scripts\python.exe"
    $backendInstallMarker = Join-Path $venvPath ".installed.marker"
    $frontendInstallMarker = Join-Path $frontendPath ".installed.marker"

    # Check Python
    try {
        $pyCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pyCmd) { throw "Python not found on PATH. Please install Python 3.8+ and ensure 'python' is on PATH." }
        $pyVersion = (& python --version) -replace '\r|\n',''
        Write-OK "Python detected: $pyVersion"
    } catch {
        Write-Err $_.Exception.Message
        exit 1
    }

    # Check Node.js
    try {
        $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
        if (-not $nodeCmd) { throw "Node.js not found on PATH. Please install Node.js and ensure 'node' is on PATH." }
        $nodeVersion = (& node --version) -replace '\r|\n',''
        Write-OK "Node.js detected: $nodeVersion"
    } catch {
        Write-Err $_.Exception.Message
        exit 1
    }

    # Ensure backend folder exists
    if (-not (Test-Path $backendPath)) {
        Write-Err "Backend folder not found at $backendPath"
        exit 1
    }

    # Create virtual environment if missing
    if (-not (Test-Path $venvPath)) {
        Write-Host "Creating virtual environment in $venvPath..."
        try {
            & python -m venv $venvPath
            Write-OK "Virtual environment created."
        } catch {
            Write-Err "Failed to create virtualenv: $($_.Exception.Message)"
            exit 1
        }
    } else {
        Write-Warn "Virtual environment already exists; skipping creation."
    }

    # Activate virtual environment (dot-source)
    try {
        $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
        if (Test-Path $activateScript) {
            . $activateScript
            Write-OK "Activated virtual environment."
        } else {
            Write-Warn "Activate script not found; using venv python directly."
        }
    } catch {
        Write-Warn "Could not dot-source Activate.ps1: $($_.Exception.Message)"
    }

    # Use venv python explicitly for installs
    if (-not (Test-Path $venvPython)) {
        Write-Warn "Using 'python' from PATH for installs because venv python not found."
        $venvPython = (Get-Command python).Source
    }

    # Upgrade pip inside venv
    try {
        Write-Host "Upgrading pip..."
        & $venvPython -m pip install --upgrade pip setuptools wheel | Out-Null
        Write-OK "pip upgraded."
    } catch {
        Write-Warn "pip upgrade failed: $($_.Exception.Message)"
    }

    # Install backend dependencies if not already installed (marker prevents duplicates)
    Set-Location $backendPath
    if (-not (Test-Path $backendInstallMarker)) {
        try {
            Write-Host "Installing backend dependencies from requirements.txt..."
            & $venvPython -m pip install -r requirements.txt 2>&1 | Tee-Object -Variable pipOut
            Write-OK "Attempted pip install for backend."
            if ($LASTEXITCODE -ne 0) {
                Write-Warn "pip reported non-zero exit code. Attempting per-package install to recover..."
                $reqs = Get-Content requirements.txt | Where-Object { $_ -and -not ($_ -match '^\s*#') }
                foreach ($pkg in $reqs) {
                    try {
                        & $venvPython -m pip install $pkg
                    } catch {
                        Write-Warn "Failed to install package '$pkg': $($_.Exception.Message)"
                    }
                }
            }
            New-Item -Path $backendInstallMarker -ItemType File -Force | Out-Null
            Write-OK "Backend dependencies installed (marker created)."
        } catch {
            Write-Err "Failed backend dependency installation: $($_.Exception.Message)"
            exit 1
        }
    } else {
        Write-Warn "Backend dependencies already installed (marker present)."
    }

    # Quick CORS auto-check
    try {
        $corsFound = Get-ChildItem -Path (Join-Path $backendPath "app") -Recurse -Include *.py -ErrorAction SilentlyContinue |
                     Select-String -Pattern "CORSMiddleware" -SimpleMatch -Quiet
        if (-not $corsFound) {
            Write-Warn "CORS middleware not detected in backend application. Cross-origin requests may be blocked."
        } else {
            Write-OK "CORS middleware detected."
        }
    } catch {
        Write-Warn "Unable to perform CORS check: $($_.Exception.Message)"
    }

    # Start backend
    Write-Host "Starting backend (uvicorn) on port 8000..."
    try {
        $uvicornArgs = @('-m','uvicorn','app.main:app','--host','0.0.0.0','--port','8000')
        $backendProc = Start-Process -FilePath $venvPython -ArgumentList $uvicornArgs -WorkingDirectory $backendPath -WindowStyle Minimized -PassThru
        Write-OK "Backend process started (PID $($backendProc.Id))."
    } catch {
        Write-Err "Failed to start backend: $($_.Exception.Message)"
        exit 1
    }

    # Wait for backend port 8000 to be ready
    function Test-PortOpen { param($host,$port) try { $t = Test-NetConnection -ComputerName $host -Port $port -WarningAction SilentlyContinue; return $t.TcpTestSucceeded } catch { return $false } }
    $waitSeconds = 60
    $elapsed = 0
    while ($elapsed -lt $waitSeconds) {
        if (Test-PortOpen -host '127.0.0.1' -port 8000) {
            Write-OK "Backend is listening on port 8000."
            break
        }
        Start-Sleep -Seconds 1
        $elapsed++
    }
    if ($elapsed -ge $waitSeconds) {
        Write-Err "Timed out waiting for backend port 8000."
        # Optionally capture logs or dump process info
        if ($backendProc -and -not $backendProc.HasExited) {
            Write-Warn "Backend PID $($backendProc.Id) still running; check logs in $backendPath."
        }
        exit 1
    }

    # Frontend setup
    if (-not (Test-Path $frontendPath)) {
        Write-Err "Frontend folder not found at $frontendPath"
        exit 1
    }
    Set-Location $frontendPath

    if (-not (Test-Path $frontendInstallMarker)) {
        try {
            Write-Host "Running npm install in frontend..."
            $npmInstall = Start-Process -FilePath 'npm' -ArgumentList 'install' -WorkingDirectory $frontendPath -NoNewWindow -Wait -PassThru
            if ($npmInstall.ExitCode -ne 0) {
                Write-Warn "npm install failed (exit code $($npmInstall.ExitCode)). Trying legacy-peer-deps..."
                $npmInstall2 = Start-Process -FilePath 'npm' -ArgumentList 'install','--legacy-peer-deps' -WorkingDirectory $frontendPath -NoNewWindow -Wait -PassThru
                if ($npmInstall2.ExitCode -ne 0) {
                    Write-Warn "npm install with legacy-peer-deps failed. Attempting audit fix..."
                    Start-Process -FilePath 'npm' -ArgumentList 'audit','fix','--force' -WorkingDirectory $frontendPath -NoNewWindow -Wait -PassThru | Out-Null
                }
            }
            New-Item -Path $frontendInstallMarker -ItemType File -Force | Out-Null
            Write-OK "Frontend dependencies installed (marker created)."
        } catch {
            Write-Err "Failed frontend install: $($_.Exception.Message)"
            exit 1
        }
    } else {
        Write-Warn "Frontend dependencies already installed (marker present)."
    }

    # Start frontend
    Write-Host "Starting frontend (npm start)..."
    try {
        $frontendProc = Start-Process -FilePath 'npm' -ArgumentList 'start' -WorkingDirectory $frontendPath -WindowStyle Minimized -PassThru
        Write-OK "Frontend process started (PID $($frontendProc.Id))."
    } catch {
        Write-Err "Failed to start frontend: $($_.Exception.Message)"
        # Try to stop backend before exiting
        if ($backendProc -and -not $backendProc.HasExited) { Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue }
        exit 1
    }

    # Wait a short while and then open browser to frontend
    Start-Sleep -Seconds 3
    $browserUrl = "http://localhost:3000"
    try {
        Start-Process $browserUrl
        Write-OK "Opened default browser to $browserUrl"
    } catch {
        Write-Warn "Unable to auto-open browser: $($_.Exception.Message)"
    }

    # Register Ctrl+C handler for graceful shutdown
    $shutdownAction = {
        param($sender,$eventArgs)
        Write-Host "`nShutdown requested. Stopping services..." -ForegroundColor Cyan
        try {
            if ($script:frontendProc -and -not $script:frontendProc.HasExited) {
                Write-Host "Stopping frontend (PID $($script:frontendProc.Id))..." -ForegroundColor Yellow
                Stop-Process -Id $script:frontendProc.Id -Force -ErrorAction SilentlyContinue
                Write-OK "Frontend stopped."
            }
            if ($script:backendProc -and -not $script:backendProc.HasExited) {
                Write-Host "Stopping backend (PID $($script:backendProc.Id))..." -ForegroundColor Yellow
                Stop-Process -Id $script:backendProc.Id -Force -ErrorAction SilentlyContinue
                Write-OK "Backend stopped."
            }
        } catch {
            Write-Warn "Errors during shutdown: $($_.Exception.Message)"
        } finally {
            Write-OK "Shutdown complete."
            # Allow script to exit
            exit 0
        }
    }
    Register-ObjectEvent -InputObject [Console] -EventName CancelKeyPress -Action $shutdownAction | Out-Null

    Write-Host "`nServices are running. Press CTRL+C to stop." -ForegroundColor Cyan

    # Keep script alive while processes run
    while ($true) {
        Start-Sleep -Seconds 2
        if ($backendProc -and $backendProc.HasExited) {
            Write-Err "Backend process has exited unexpectedly. Stopping frontend..."
            if ($frontendProc -and -not $frontendProc.HasExited) { Stop-Process -Id $frontendProc.Id -Force -ErrorAction SilentlyContinue }
            exit 1
        }
        if ($frontendProc -and $frontendProc.HasExited) {
            Write-Warn "Frontend process exited. Backend running. Press CTRL+C to stop or restart manually."
            break
        }
    }

} catch {
    Write-Err "Fatal error: $($_.Exception.Message)"
    exit 1
}
