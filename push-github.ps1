# Push this project to https://github.com/mohmwvel/project72-unsw-nb15
# Requires: GitHub CLI (gh). Install: winget install GitHub.cli
# Then EITHER run `gh auth login` once OR set GH_TOKEN for this session.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$OwnerRepo = "mohmwvel/project72-unsw-nb15"
$RemoteUrl = "https://github.com/$OwnerRepo.git"

function Test-GhAuth {
    gh auth status 2>&1 | Out-Null
    return ($LASTEXITCODE -eq 0)
}

if (-not (Test-GhAuth)) {
    if ($env:GH_TOKEN -or $env:GITHUB_TOKEN) {
        $tok = if ($env:GH_TOKEN) { $env:GH_TOKEN } else { $env:GITHUB_TOKEN }
        $tok | gh auth login --with-token
    }
    else {
        Write-Host ""
        Write-Host "GitHub CLI is not logged in." -ForegroundColor Yellow
        Write-Host "  Option A: run this in a terminal, then run this script again:" -ForegroundColor Cyan
        Write-Host "            gh auth login" -ForegroundColor White
        Write-Host "  Option B: create a token (repo scope) at https://github.com/settings/tokens" -ForegroundColor Cyan
        Write-Host "            then in PowerShell:" -ForegroundColor Cyan
        Write-Host '            $env:GH_TOKEN = "paste_token_here"' -ForegroundColor White
        Write-Host "            .\push-github.ps1" -ForegroundColor White
        Write-Host ""
        exit 1
    }
}

if (-not (Test-GhAuth)) {
    Write-Error "Still not authenticated. Fix auth and re-run."
    exit 1
}

# Repo already on GitHub?
$exists = $false
gh repo view $OwnerRepo 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { $exists = $true }

if ($exists) {
    Write-Host "Remote repo exists. Configuring origin and pushing..."
    git remote remove origin 2>$null
    git remote add origin $RemoteUrl
    git push -u origin main
}
else {
    Write-Host "Creating GitHub repo $OwnerRepo and pushing..."
    git remote remove origin 2>$null
    gh repo create $OwnerRepo `
        --public `
        --description "UNSW-NB15 intrusion detection — Random Forest (Project 72)" `
        --source=. `
        --remote=origin `
        --push
}

Write-Host ""
Write-Host "Done. Repo: https://github.com/$OwnerRepo" -ForegroundColor Green
