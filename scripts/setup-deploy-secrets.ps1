# Setup GitHub Actions deploy secrets for vagushub
# Run: gh auth login   (first, if not already logged in)
# Then: .\scripts\setup-deploy-secrets.ps1

$ErrorActionPreference = "Stop"
$repo = "ultradaoto/vagushub"

# Check gh is available (try PATH first, then temp install)
$ghExe = (Get-Command gh -ErrorAction SilentlyContinue).Source
if (-not $ghExe) {
    $ghExe = "$env:TEMP\gh_cli\bin\gh.exe"
}
if (-not (Test-Path $ghExe)) {
    Write-Host "Install GitHub CLI: winget install GitHub.cli" -ForegroundColor Yellow
    Write-Host "Or download from: https://cli.github.com/" -ForegroundColor Yellow
    exit 1
}

# Check auth
$auth = & $ghExe auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Run: gh auth login" -ForegroundColor Yellow
    exit 1
}

$keyPath = "$env:USERPROFILE\.ssh\id_ed25519"
if (-not (Test-Path $keyPath)) {
    Write-Host "SSH key not found at $keyPath" -ForegroundColor Red
    exit 1
}

$keyContent = Get-Content $keyPath -Raw
& $ghExe secret set SSH_PRIVATE_KEY --repo $repo --body $keyContent
& $ghExe secret set REMOTE_HOST --repo $repo --body "143.198.103.15"
& $ghExe secret set REMOTE_USER --repo $repo --body "deployer"
& $ghExe secret set REMOTE_PORT --repo $repo --body "22"

Write-Host "Secrets configured. Re-run the failed workflow or push to trigger deploy." -ForegroundColor Green
