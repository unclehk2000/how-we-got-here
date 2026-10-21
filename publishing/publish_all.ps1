# Publishes every indicator folder next to this script as its own PUBLIC GitHub repository.
# Needs Git and the GitHub CLI (gh), signed in once with:  gh auth login
# Safe to run again: repos that already exist on your account are skipped.
# Run from PowerShell:  powershell -ExecutionPolicy Bypass -File .\publish_all.ps1

$ErrorActionPreference = 'Continue'
$here = $PSScriptRoot
Set-Location -LiteralPath $here

foreach ($tool in @('git', 'gh')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Host "Missing: $tool. Install Git (https://git-scm.com) and the GitHub CLI (https://cli.github.com), then run this again." -ForegroundColor Red
        exit 1
    }
}
gh auth status *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not signed in to GitHub. Run:  gh auth login   then run this again." -ForegroundColor Red
    exit 1
}

$login = "$(gh api user --jq .login)".Trim()
$uid   = "$(gh api user --jq .id)".Trim()
$gName  = "$(git config --global user.name)".Trim()
$gEmail = "$(git config --global user.email)".Trim()
Write-Host "Publishing to github.com/$login" -ForegroundColor Cyan

$topics = @('tradingview', 'pine-script', 'pinescript', 'trading-indicators', 'futures', 'nasdaq')
$repos  = Import-Csv -LiteralPath (Join-Path $here 'repos.csv') -Encoding UTF8
$made = 0; $skipped = 0; $failed = @()

foreach ($r in $repos) {
    $slug = $r.slug
    $dir  = Join-Path $here $slug
    if (-not (Test-Path -LiteralPath $dir)) { Write-Host "skip  $slug (folder missing)"; $skipped++; continue }

    gh repo view "$login/$slug" *> $null
    if ($LASTEXITCODE -eq 0) { Write-Host "skip  $slug (already on GitHub)" -ForegroundColor Yellow; $skipped++; continue }

    Push-Location -LiteralPath $dir
    try {
        if (-not (Test-Path -LiteralPath '.git')) {
            git init -q
            if (-not $gName)  { git config user.name $login }
            if (-not $gEmail) { git config user.email "$uid+$login@users.noreply.github.com" }
            git add -A
            git commit -q -m "Initial commit: $slug (TradingView Pine Script v6)"
            git branch -M main
        }
        git remote get-url origin *> $null
        if ($LASTEXITCODE -eq 0) { git remote remove origin }

        gh repo create $slug --public --description "$($r.description)" --source . --remote origin --push
        if ($LASTEXITCODE -ne 0) { throw "gh repo create failed" }
        foreach ($t in $topics) { gh repo edit "$login/$slug" --add-topic $t *> $null }
        Write-Host "done  $slug  ->  https://github.com/$login/$slug" -ForegroundColor Green
        $made++
    }
    catch {
        Write-Host "FAIL  $slug : $_" -ForegroundColor Red
        $failed += $slug
    }
    finally { Pop-Location }
}

Write-Host ""
Write-Host "Created $made, skipped $skipped, failed $($failed.Count)." -ForegroundColor Cyan
if ($failed.Count -gt 0) { Write-Host "Failed: $($failed -join ', '). Fix the message above and run this again; finished repos are skipped." -ForegroundColor Red; exit 1 }
