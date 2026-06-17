param(
    [string]$Python = "python",
    [string]$Name = "8PuzzleSearchLab"
)

$ErrorActionPreference = "Stop"

Write-Host "Building desktop app with $Python"
& $Python -m PyInstaller --clean --noconfirm --windowed --onefile `
    --name $Name `
    --collect-submodules eight_puzzle_tk `
    .\eight_puzzle_tk_app.py

Write-Host ""
Write-Host "Done. EXE:"
Write-Host "  .\dist\$Name.exe"
