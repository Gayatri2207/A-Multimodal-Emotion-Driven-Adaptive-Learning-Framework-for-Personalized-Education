#!/usr/bin/env pwsh
<#
.SYNOPSIS
Pre-flight verification script for Emotion-Adaptive Learning System

.DESCRIPTION
Checks all dependencies and configuration before running the main startup script
#>

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║ Emotion-Adaptive Learning System - PRE-FLIGHT CHECK      ║" -ForegroundColor Magenta
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

$allGood = $true

# Check Python
Write-Host "📋 Python 3.12+... " -NoNewline
try {
    $pyVersion = python --version 2>&1
    if ($pyVersion -match "3.1[2-9]|3.[2-9][0-9]|4.\d") {
        Write-Host "✓ $pyVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Found $pyVersion (need 3.12+)" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "✗ Not found on PATH" -ForegroundColor Red
    $allGood = $false
}

# Check Node
Write-Host "📋 Node.js 18+... " -NoNewline
$nodeFound = $false
if (Test-Path "C:\Program Files\nodejs\node.exe") {
    $nodeVersion = & "C:\Program Files\nodejs\node.exe" --version
    if ($nodeVersion -match "v(1[8-9]|[2-9]\d)") {
        Write-Host "✓ $nodeVersion" -ForegroundColor Green
        $nodeFound = $true
    }
} else {
    try {
        $nodeVersion = node --version
        if ($nodeVersion -match "v(1[8-9]|[2-9]\d)") {
            Write-Host "✓ $nodeVersion" -ForegroundColor Green
            $nodeFound = $true
        }
    } catch { }
}
if (-not $nodeFound) {
    Write-Host "✗ Not found" -ForegroundColor Red
    $allGood = $false
}

# Check npm
Write-Host "📋 npm 9+... " -NoNewline
try {
    $npmVersion = npm --version
    if ($npmVersion -match "(9|10|11|12|13|14|15|16|17|18|19|[2-9]\d)") {
        Write-Host "✓ $npmVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Found $npmVersion (need 9+)" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "✗ Not found" -ForegroundColor Red
    $allGood = $false
}

# Check backend structure
Write-Host "📁 Backend directory... " -NoNewline
if (Test-Path "backend\app\main.py") {
    Write-Host "✓ Found" -ForegroundColor Green
} else {
    Write-Host "✗ Missing backend/app/main.py" -ForegroundColor Red
    $allGood = $false
}

# Check frontend structure
Write-Host "📁 Frontend directory... " -NoNewline
if (Test-Path "frontend_app\src\App.js") {
    Write-Host "✓ Found" -ForegroundColor Green
} else {
    Write-Host "✗ Missing frontend_app/src/App.js" -ForegroundColor Red
    $allGood = $false
}

# Check requirements.txt
Write-Host "📋 Backend requirements... " -NoNewline
if (Test-Path "backend\requirements.txt") {
    $reqCount = @(Get-Content backend\requirements.txt | Where-Object { $_ -and -not ($_ -match "^\s*#") }).Count
    Write-Host "✓ $reqCount packages" -ForegroundColor Green
} else {
    Write-Host "✗ Missing backend/requirements.txt" -ForegroundColor Red
    $allGood = $false
}

# Check package.json
Write-Host "📋 Frontend package.json... " -NoNewline
if (Test-Path "frontend_app\package.json") {
    Write-Host "✓ Found" -ForegroundColor Green
} else {
    Write-Host "✗ Missing frontend_app/package.json" -ForegroundColor Red
    $allGood = $false
}

# Check startup script
Write-Host "📋 Startup script... " -NoNewline
if (Test-Path "run_project.ps1") {
    Write-Host "✓ Found" -ForegroundColor Green
} else {
    Write-Host "✗ Missing run_project.ps1" -ForegroundColor Red
    $allGood = $false
}

# Port availability
Write-Host "🔌 Port 8000 available... " -NoNewline
$portTest = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue
if (-not $portTest.TcpTestSucceeded) {
    Write-Host "✓ Available" -ForegroundColor Green
} else {
    Write-Host "⚠ In use (will stop existing process)" -ForegroundColor Yellow
}

Write-Host "🔌 Port 3000 available... " -NoNewline
$portTest = Test-NetConnection -ComputerName 127.0.0.1 -Port 3000 -WarningAction SilentlyContinue
if (-not $portTest.TcpTestSucceeded) {
    Write-Host "✓ Available" -ForegroundColor Green
} else {
    Write-Host "⚠ In use (will stop existing process)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" + ("─" * 60)
if ($allGood) {
    Write-Host "✓ ALL CHECKS PASSED - Ready to start!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Run this to start the system:" -ForegroundColor Cyan
    Write-Host "  powershell -ExecutionPolicy Bypass -File run_project.ps1" -ForegroundColor Green
} else {
    Write-Host "✗ SOME CHECKS FAILED - Please fix issues above" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install missing components from:" -ForegroundColor Yellow
    Write-Host "  Python:  https://www.python.org/downloads/" -ForegroundColor Gray
    Write-Host "  Node.js: https://nodejs.org/" -ForegroundColor Gray
}
Write-Host ("─" * 60) + "`n"
