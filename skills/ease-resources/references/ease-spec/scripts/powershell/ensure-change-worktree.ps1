#!/usr/bin/env pwsh
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9]{3}-[a-z0-9][a-z0-9-]*$')]
    [string]$ChangeId,

    [ValidateSet("auto", "required", "reuse", "off")]
    [string]$Policy = "auto",

    [string]$Base = "",
    [string]$Repo = ".",
    [string]$WorktreeRoot = ""
)

$ErrorActionPreference = "Stop"

function Write-Result {
    param(
        [string]$Status,
        [string]$Branch,
        [string]$WorktreePath,
        [string]$BaseBranch = ""
    )

    $isolationStatus = if ($Policy -eq "off") { "waived" } else { "active" }
    [ordered]@{
        status           = $Status
        policy           = $Policy
        change_id        = $ChangeId
        branch           = $Branch
        worktree_path    = $WorktreePath
        base_branch      = $BaseBranch
        isolation_status = $isolationStatus
    } | ConvertTo-Json -Compress
}

function Stop-WithError {
    param(
        [string]$Id,
        [string]$Message,
        [int]$ExitCode = 3
    )

    $payload = [ordered]@{
        error     = $Id
        policy    = $Policy
        change_id = $ChangeId
        message   = $Message
    } | ConvertTo-Json -Compress
    [Console]::Error.WriteLine($payload)
    exit $ExitCode
}

function Test-GitRef {
    param([string]$Ref)
    & git -C $script:RepoRoot show-ref --verify --quiet $Ref 2>$null
    return $LASTEXITCODE -eq 0
}

function Resolve-BaseRef {
    if ($Base) {
        if (Test-GitRef "refs/heads/$Base") { return $Base }
        if (Test-GitRef "refs/remotes/origin/$Base") { return "origin/$Base" }
        Stop-WithError "base-branch-not-found" "Base branch '$Base' does not exist locally or on origin"
    }

    foreach ($candidate in @("develop", "main", "master")) {
        if (Test-GitRef "refs/heads/$candidate") { return $candidate }
        if (Test-GitRef "refs/remotes/origin/$candidate") { return "origin/$candidate" }
    }
    Stop-WithError "base-branch-not-found" "No develop, main, or master branch is available"
}

function Find-BranchWorktree {
    param([string]$Branch)

    $path = ""
    $target = "branch refs/heads/$Branch"
    $lines = & git -C $script:RepoRoot worktree list --porcelain
    foreach ($line in $lines) {
        if ($line.StartsWith("worktree ")) {
            $path = $line.Substring(9)
        } elseif ($line -eq $target) {
            return $path
        }
    }
    return ""
}

$resolvedRoot = & git -C $Repo rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -ne 0 -or -not $resolvedRoot) {
    Stop-WithError "not-a-git-repository" "The requested path is not inside a Git worktree" 2
}
$script:RepoRoot = ($resolvedRoot | Select-Object -First 1).Trim()
$targetBranch = "feature/$ChangeId"
$currentBranchOutput = & git -C $script:RepoRoot branch --show-current
$currentBranch = "$currentBranchOutput".Trim()
if (-not $currentBranch) { $currentBranch = "DETACHED" }

if ($Policy -eq "off") {
    Write-Result "skipped" $currentBranch $script:RepoRoot
    exit 0
}

if ($currentBranch -eq $targetBranch) {
    Write-Result "reused-current" $targetBranch $script:RepoRoot
    exit 0
}

if ($Policy -eq "required") {
    Stop-WithError "target-worktree-required" "Current branch '$currentBranch' is not '$targetBranch'"
}

if ($currentBranch.StartsWith("feature/")) {
    Stop-WithError "branch-conflict" "Current feature branch '$currentBranch' does not match '$targetBranch'"
}

$existingWorktree = Find-BranchWorktree $targetBranch
if ($existingWorktree) {
    Write-Result "existing-worktree" $targetBranch $existingWorktree
    exit 0
}

if ($Policy -eq "reuse") {
    Stop-WithError "worktree-not-found" "No worktree is registered for '$targetBranch'"
}

$dirty = & git -C $script:RepoRoot status --porcelain
if ($dirty) {
    Stop-WithError "dirty-working-tree" "Commit or stash current changes before creating '$targetBranch'"
}

if (-not $WorktreeRoot) {
    $parent = Split-Path $script:RepoRoot -Parent
    $repositoryName = Split-Path $script:RepoRoot -Leaf
    $WorktreeRoot = Join-Path (Join-Path $parent ".ease-worktrees") $repositoryName
} else {
    $WorktreeRoot = [System.IO.Path]::GetFullPath($WorktreeRoot)
}
$targetPath = Join-Path (Join-Path $WorktreeRoot "feature") $ChangeId
New-Item -ItemType Directory -Force -Path (Split-Path $targetPath -Parent) | Out-Null

if (Test-GitRef "refs/heads/$targetBranch") {
    & git -C $script:RepoRoot worktree add $targetPath $targetBranch | Out-Null
    if ($LASTEXITCODE -ne 0) { Stop-WithError "worktree-create-failed" "Could not attach '$targetBranch'" }
    Write-Result "attached" $targetBranch $targetPath
    exit 0
}

if (Test-GitRef "refs/remotes/origin/$targetBranch") {
    & git -C $script:RepoRoot worktree add --track -b $targetBranch $targetPath "origin/$targetBranch" | Out-Null
    if ($LASTEXITCODE -ne 0) { Stop-WithError "worktree-create-failed" "Could not attach origin/$targetBranch" }
    Write-Result "attached-remote" $targetBranch $targetPath "origin/$targetBranch"
    exit 0
}

$baseRef = Resolve-BaseRef
& git -C $script:RepoRoot worktree add -b $targetBranch $targetPath $baseRef | Out-Null
if ($LASTEXITCODE -ne 0) { Stop-WithError "worktree-create-failed" "Could not create '$targetBranch' from '$baseRef'" }
Write-Result "created" $targetBranch $targetPath $baseRef
