# Seed the public backlog: create milestones (with due dates) and file every
# draft in .github/ISSUE_DRAFTS/ as a GitHub issue.
#
# Idempotent: drafts whose title already exists as an open issue are skipped,
# milestones that already exist are left alone.

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$RepoRoot   = Resolve-Path (Join-Path $PSScriptRoot '..')
$DraftsDir  = Join-Path $RepoRoot '.github/ISSUE_DRAFTS'

# ---- Milestones --------------------------------------------------------------
$Milestones = @(
    @{ Title = 'v1.0.1'; Due = '2026-06-04T23:59:59Z'; Description = 'Polish: docs, demo, snapshot tests, CLI fix' }
    @{ Title = 'v1.1.0'; Due = '2026-07-09T23:59:59Z'; Description = 'Coverage: new model adapters + UX' }
    @{ Title = 'v1.2.0'; Due = '2026-08-20T23:59:59Z'; Description = 'Scale: new tasks + async evaluation' }
    @{ Title = 'v1.3.0'; Due = '2026-10-29T23:59:59Z'; Description = 'Research: architecture studies' }
)

# ---- Preflight ---------------------------------------------------------------
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "gh (GitHub CLI) is required. Install from https://cli.github.com/"
}

try { gh auth status 2>&1 | Out-Null } catch {
    throw "gh is not authenticated. Run 'gh auth login' first."
}

$Repo = gh repo view --json nameWithOwner -q .nameWithOwner
Write-Host "==> Repo: $Repo"

# ---- Create milestones -------------------------------------------------------
$existingMilestones = gh api "repos/$Repo/milestones?state=all" --paginate `
    | ConvertFrom-Json

$existingTitles = @($existingMilestones | ForEach-Object { $_.title })

foreach ($m in $Milestones) {
    if ($existingTitles -contains $m.Title) {
        Write-Host "    milestone exists: $($m.Title)"
    } else {
        Write-Host "    creating milestone: $($m.Title) (due $($m.Due))"
        gh api "repos/$Repo/milestones" `
            -f title="$($m.Title)" `
            -f state="open" `
            -f description="$($m.Description)" `
            -f due_on="$($m.Due)" | Out-Null
    }
}

# Rebuild title -> number map after creation
$milestoneMap = @{}
$allMilestones = gh api "repos/$Repo/milestones?state=all" --paginate | ConvertFrom-Json
foreach ($ms in $allMilestones) { $milestoneMap[$ms.title] = $ms.number }

# ---- File issues -------------------------------------------------------------
$existingIssues = gh issue list --state all --limit 500 --json title `
    | ConvertFrom-Json
$existingIssueTitles = @($existingIssues | ForEach-Object { $_.title })

function Parse-Frontmatter {
    param([string]$Path)

    $lines = Get-Content -LiteralPath $Path
    $fmStart = -1; $fmEnd = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -eq '---') {
            if ($fmStart -lt 0) { $fmStart = $i }
            elseif ($fmEnd -lt 0) { $fmEnd = $i; break }
        }
    }
    if ($fmStart -lt 0 -or $fmEnd -lt 0) { return $null }

    $fmLines = $lines[($fmStart + 1)..($fmEnd - 1)]
    $bodyLines = if ($fmEnd + 1 -le $lines.Count - 1) {
        $lines[($fmEnd + 1)..($lines.Count - 1)]
    } else { @() }

    $title = $null; $milestone = $null; $labels = @()
    $inLabels = $false
    foreach ($line in $fmLines) {
        if ($line -match '^title:\s*"(.*)"\s*$') { $title = $Matches[1]; $inLabels = $false; continue }
        if ($line -match '^milestone:\s*"(.*)"\s*$') { $milestone = $Matches[1]; $inLabels = $false; continue }
        if ($line -match '^labels:\s*$') { $inLabels = $true; continue }
        if ($inLabels -and $line -match '^\s*-\s*(.+?)\s*$') { $labels += $Matches[1]; continue }
        if ($line -match '^\S') { $inLabels = $false }
    }

    return [pscustomobject]@{
        Title     = $title
        Milestone = $milestone
        Labels    = $labels
        Body      = ($bodyLines -join "`n").TrimStart("`n")
    }
}

Get-ChildItem -LiteralPath $DraftsDir -Filter '*.md' | Where-Object { $_.Name -ne 'README.md' } | ForEach-Object {
    $draft = $_
    $parsed = Parse-Frontmatter -Path $draft.FullName
    if ($null -eq $parsed -or [string]::IsNullOrWhiteSpace($parsed.Title)) {
        Write-Warning "skip $($draft.Name): no title"
        return
    }

    if ($existingIssueTitles -contains $parsed.Title) {
        Write-Host "    issue exists: $($parsed.Title)"
        return
    }

    Write-Host "==> filing: $($parsed.Title)"

    $bodyFile = New-TemporaryFile
    try {
        Set-Content -LiteralPath $bodyFile -Value $parsed.Body -Encoding utf8

        $args = @('issue', 'create', '--title', $parsed.Title, '--body-file', $bodyFile)
        if ($parsed.Labels.Count -gt 0) {
            $args += '--label'
            $args += ($parsed.Labels -join ',')
        }
        if ($parsed.Milestone -and $milestoneMap.ContainsKey($parsed.Milestone)) {
            $args += '--milestone'
            $args += $parsed.Milestone
        } elseif ($parsed.Milestone) {
            Write-Warning "milestone '$($parsed.Milestone)' not found for $($draft.Name); filing without milestone"
        }

        & gh @args
    } finally {
        Remove-Item -LiteralPath $bodyFile -ErrorAction SilentlyContinue
    }
}

Write-Host "==> done."
