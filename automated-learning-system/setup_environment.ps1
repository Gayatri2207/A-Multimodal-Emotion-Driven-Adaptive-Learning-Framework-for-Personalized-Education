<#
.SYNOPSIS
Setup script for Emotion-Adaptive Learning Platform.
Installs Python dependencies, Node packages, downloads ML models, and configures .env.
#>

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host ">>> $Message" -ForegroundColor Cyan
}

function Write-OK {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "   ENVIRONMENT SETUP SCRIPT" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

# -------------------------------------------------------
# 1. CREATE .env FILE
# -------------------------------------------------------
Write-Step "Creating Backend .env Configuration..."
$envFile = Join-Path "backend" ".env"
if (-not (Test-Path $envFile)) {
    $envContent = @"
DATABASE_URL=sqlite:///./emotion_learning.db
SECRET_KEY=supersecretkey-change-in-production
RL_MODEL_PATH=./models/ppo_model.zip
"@
    $envContent | Out-File -FilePath $envFile -Encoding utf8
    Write-OK "Created $envFile"
} else {
    Write-OK ".env already exists, skipping."
}

# -------------------------------------------------------
# 2. PYTHON VIRTUAL ENV & DEPENDENCIES
# -------------------------------------------------------
Write-Step "Setting up Python Environment..."
Set-Location "backend"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-OK "Virtual environment created."
} else {
    Write-OK "Virtual environment already exists."
}

& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt
Write-OK "Python dependencies installed."

# -------------------------------------------------------
# 3. DOWNLOAD HUGGINGFACE MODELS
# -------------------------------------------------------
Write-Step "Downloading Pretrained HuggingFace Models..."

$pythonScript = @"
try:
    from transformers import Wav2Vec2Processor, Wav2Vec2ForSequenceClassification
    print('Downloading superb/wav2vec2-base-superb-er ...')
    Wav2Vec2Processor.from_pretrained('superb/wav2vec2-base-superb-er')
    Wav2Vec2ForSequenceClassification.from_pretrained('superb/wav2vec2-base-superb-er')
    print('Model cached successfully.')
except Exception as e:
    print('Model download failed (non-critical):', e)
"@

$tempScript = [System.IO.Path]::GetTempFileName() + ".py"
$pythonScript | Out-File -FilePath $tempScript -Encoding utf8
python $tempScript
Remove-Item $tempScript -ErrorAction SilentlyContinue

Write-OK "HuggingFace models step complete."
Set-Location ".."

# -------------------------------------------------------
# 4. FRONTEND NODE DEPENDENCIES
# -------------------------------------------------------
Write-Step "Installing Frontend Node.js Dependencies..."
Set-Location "frontend_app"

npm install --legacy-peer-deps
npm install chart.js recharts socket.io-client --legacy-peer-deps

Write-OK "Node dependencies installed."
Set-Location ".."

# -------------------------------------------------------
# 5. DONE
# -------------------------------------------------------
Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "[OK] SETUP COMPLETE. System is ready!" -ForegroundColor Green
Write-Host "Now run: .\start_emotion_system.ps1" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta