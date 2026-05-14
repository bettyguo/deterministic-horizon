# Back-fill labels and milestones on issues that were filed before the
# labels/milestones existed. Idempotent: skips any state that's already in
# place.
#
# Run from anywhere; the script resolves the drafts directory relative to its
# own location.

[CmdletBinding()]
param(
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$RepoRoot  = Resolve-Path (Join-Path $PSScriptRoot '..')
$DraftsDir = Join-Path $RepoRoot '.github/ISSUE_DRAFTS'

# ---- Labels we expect the drafts to reference --------------------------------
$LabelSpec = @(
    # rename map: GitHub default name -> desired name (drafts use hyphens)
    @{ Action='rename'; From='good first issue'; To='good-first-issue' }
    @{ Action='rename'; From='help wanted';      To='help-wanted' }

    # custom labels the drafts depend on
    @{ Action='create'; Name='tests';              Color='c5def5'; Description='Test coverage and quality' }
    @{ Action='create'; Name='models';             Color='5319e7'; Description='Model adapters' }
    @{ Action='create'; Name='reliability';        Color='fbca04'; Description='Resilience and recoverability' }
    @{ Action='create'; Name='demo';               Color='fef2c0'; Description='Demos and showcase' }
    @{ Action='create'; Name='i18n';               Color='bfdadc'; Description='Internationalisation / translations' }
    @{ Action='create'; Name='research';           Color='1d76db'; Description='Research / paper-grade work' }
    @{ Action='create'; Name='new-task';           Color='0e8a16'; Description='New benchmark task' }
    @{ Action='create'; Name='performance';        Color='f9d0c4'; Description='Performance / throughput' }
    @{ Action='create'; Name='architecture-study'; Color='8a2be2'; Description='Architecture-comparison study' }
)

# ---- Milestones --------------------------------------------------------------
$Milestones = @(
    @{ Title = 'v1.0.1'; Due = '2026-06-04T23:59:59Z'; Description = 'Polish: docs, demo, snapshot tests, CLI fix' }
    @{ Title = 'v1.1.0'; Due = '2026-07-09T23:59:59Z'; Description = 'Coverage: new model adapters + UX' }
    @{ Title = 'v1.2.0'; Due = '2026-08-20T23:59:59Z'; Description = 'Scale: new tasks + async evaluation' }
    @{ Title = 'v1.3.0'; Due = '2026-10-29T23:59:59Z'; Description = 'Research: architecture studies' }
)

function Run-Gh {
    # NOTE: parameter is $GhArgs, not $Args — $Args is a PowerShell automatic
    # variable and using it as a parameter name silently breaks splatting.
    param([string[]]$GhArgs)
    if ($DryRun) { Write-Host "    [dry-run] gh $($GhArgs -join ' ')"; return $null }
    & gh @GhArgs
}

# ---- Preflight ---------------------------------------------------------------
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw "gh CLI not on PATH" }
try { gh auth status 2>&1 | Out-Null } catch { throw "gh not authenticated" }
$Repo = gh repo view --json nameWithOwner -q .nameWithOwner
Write-Host "==> Repo: $Repo"

# ---- 1. Labels ---------------------------------------------------------------
Write-Host "`n==> Labels"
$existing = gh label list --limit 200 --json name | ConvertFrom-Json
$existingNames = @($existing | ForEach-Object name)

foreach ($spec in $LabelSpec) {
    switch ($spec.Action) {
        'rename' {
            if ($existingNames -contains $spec.To) {
                Write-Host "    label already renamed: $($spec.To)"
            } elseif ($existingNames -contains $spec.From) {
                Write-Host "    renaming '$($spec.From)' -> '$($spec.To)'"
                Run-Gh @('label','edit',$spec.From,'--name',$spec.To)
            } else {
                Write-Host "    creating '$($spec.To)' (neither name existed)"
                Run-Gh @('label','create',$spec.To)
            }
        }
        'create' {
            if ($existingNames -contains $spec.Name) {
                Write-Host "    label exists: $($spec.Name)"
            } else {
                Write-Host "    creating label: $($spec.Name)"
                Run-Gh @('label','create',$spec.Name,'--color',$spec.Color,'--description',$spec.Description)
            }
        }
    }
}

# ---- 2. Milestones -----------------------------------------------------------
Write-Host "`n==> Milestones"
$existingMs = gh api "repos/$Repo/milestones?state=all" --paginate | ConvertFrom-Json
$existingMsTitles = @($existingMs | ForEach-Object title)

foreach ($m in $Milestones) {
    if ($existingMsTitles -contains $m.Title) {
        Write-Host "    milestone exists: $($m.Title)"
    } else {
        Write-Host "    creating milestone: $($m.Title) (due $($m.Due))"
        if (-not $DryRun) {
            gh api "repos/$Repo/milestones" `
                -f title="$($m.Title)" `
                -f state="open" `
                -f description="$($m.Description)" `
                -f due_on="$($m.Due)" | Out-Null
        }
    }
}

# ---- 3. Map issue title -> number -------------------------------------------
$allIssues = gh issue list --state all --limit 200 --json number,title,labels,milestone `
    | ConvertFrom-Json
$issueByTitle = @{}
foreach ($i in $allIssues) { $issueByTitle[$i.title] = $i }

# ---- 4. Parse front-matter and back-fill ------------------------------------
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

    $title = $null; $milestone = $null; $labels = @()
    $inLabels = $false
    foreach ($line in $fmLines) {
        if ($line -match '^title:\s*"(.*)"\s*$') { $title = $Matches[1]; $inLabels = $false; continue }
        if ($line -match '^milestone:\s*"(.*)"\s*$') { $milestone = $Matches[1]; $inLabels = $false; continue }
        if ($line -match '^labels:\s*$') { $inLabels = $true; continue }
        if ($inLabels -and $line -match '^\s*-\s*(.+?)\s*$') { $labels += $Matches[1]; continue }
        if ($line -match '^\S') { $inLabels = $false }
    }
    return [pscustomobject]@{ Title=$title; Milestone=$milestone; Labels=$labels }
}

Write-Host "`n==> Back-filling issues"
Get-ChildItem -LiteralPath $DraftsDir -Filter '*.md' `
  | Where-Object { $_.Name -ne 'README.md' } `
  | Sort-Object Name `
  | ForEach-Object {
    $parsed = Parse-Frontmatter -Path $_.FullName
    if (-not $parsed) { Write-Warning "skip $($_.Name): no front-matter"; return }

    $issue = $issueByTitle[$parsed.Title]
    if (-not $issue) {
        Write-Warning "no open issue matches title: $($parsed.Title)"
        return
    }

    $currentLabels = @($issue.labels | ForEach-Object name)
    $needLabels = @($parsed.Labels | Where-Object { $_ -and ($currentLabels -notcontains $_) })
    $currentMs = if ($issue.milestone) { $issue.milestone.title } else { $null }
    $needMs = ($parsed.Milestone -and $currentMs -ne $parsed.Milestone)

    if (-not $needLabels -and -not $needMs) {
        Write-Host "    #$($issue.number) already complete: $($parsed.Title)"
        return
    }

    $editArgs = @('issue','edit',[string]$issue.number)
    if ($needLabels) { $editArgs += '--add-label'; $editArgs += ($needLabels -join ',') }
    if ($needMs)     { $editArgs += '--milestone'; $editArgs += $parsed.Milestone }

    Write-Host "    #$($issue.number) +labels=$($needLabels -join ',') ms=$(if($needMs){$parsed.Milestone}else{'(unchanged)'})"
    Run-Gh -GhArgs $editArgs | Out-Null
}

Write-Host "`n==> done."
