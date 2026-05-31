param(
    [switch]$SkipBuild
)
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not $SkipBuild) {
    Write-Host "[build] Creating Jarvis executable bundle..."
    python .\build_jarvis.py
}

$isccCandidates = @(
    "$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
)

$iscc = $null
foreach ($candidate in $isccCandidates) {
    if (Test-Path $candidate) {
        $iscc = $candidate
        break
    }
}

if (-not $iscc) {
    $cmd = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        $iscc = $cmd.Source
    }
}

if (-not $iscc) {
    throw "Inno Setup Compiler (ISCC.exe) not found. Install Inno Setup 6 first."
}

$issFile = Join-Path $projectRoot "installer\JarvisAI.iss"
Write-Host "[build] Compiling installer using: $iscc"
& $iscc $issFile

$outputDir = Join-Path $projectRoot "installer\Output"
Write-Host "[ok] Installer build completed."
Write-Host "[out] $outputDir"
