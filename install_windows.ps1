# Robin Windows installer
$ErrorActionPreference = "Stop"

Write-Host "=== Robin Windows setup ===" -ForegroundColor Cyan

if (-not (Get-Command py -ErrorAction SilentlyContinue) -and -not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python 3.11+ is required. Install Python from python.org/downloads/windows/ and enable the PATH option."
}

$python = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }

& $python --version
& $python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host ""
Write-Host "Robin is installed." -ForegroundColor Green
Write-Host "Start it with: .\start_robin_windows.bat"
Write-Host "After Robin starts, use Remote Control in the desktop UI to display the Android pairing QR code."
