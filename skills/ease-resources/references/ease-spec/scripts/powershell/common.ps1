#!/usr/bin/env pwsh
# Common PowerShell functions analogous to common.sh

function Get-RepoRoot {
    try {
        $result = git rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $result
        }
    } catch {
        # Git command failed
    }
    
    # Fall back to script location for non-git repos
    return (Get-Location).Path
}

function Get-CurrentBranch {
    # First check if SPECIFY_FEATURE environment variable is set
    if ($env:SPECIFY_FEATURE) {
        return $env:SPECIFY_FEATURE
    }
    
    # Then check git if available
    try {
        $result = git rev-parse --abbrev-ref HEAD 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $result
        }
    } catch {
        # Git command failed
    }
    
    # For non-git repos, try to find the latest feature directory
    $repoRoot = Get-RepoRoot
    $easesDir = Join-Path $repoRoot ".eases"
    
    if (Test-Path $easesDir) {
        $latestFeature = ""
        $highest = 0
        
        Get-ChildItem -Path $easesDir -Directory | ForEach-Object {
            if ($_.Name -match '^(\d{3})-') {
                $num = [int]$matches[1]
                if ($num -gt $highest) {
                    $highest = $num
                    $latestFeature = $_.Name
                }
            }
        }
        
        if ($latestFeature) {
            return $latestFeature
        }
    }
    
    # Final fallback
    return "main"
}

function Test-HasGit {
    try {
        git rev-parse --show-toplevel 2>$null | Out-Null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Test-FeatureBranch {
    param(
        [string]$Branch,
        [bool]$HasGit = $true
    )
    
    # For non-git repos, we can't enforce branch naming but still provide output
    if (-not $HasGit) {
        Write-Warning "[specify] Warning: Git repository not detected; skipped branch validation"
        return $true
    }
    
    if ($Branch -notmatch '^[0-9]{3}-') {
        Write-Output "ERROR: Not on a feature branch. Current branch: $Branch"
        Write-Output "Feature branches should be named like: 001-feature-name"
        return $false
    }
    return $true
}

function Get-FeatureDir {
    param([string]$RepoRoot, [string]$Branch)
    Join-Path $RepoRoot ".eases/$Branch"
}
function Get-FeatureDirByPrefix {
    param([string]$RepoRoot, [string]$Branch)
    $easesDir = Join-Path $RepoRoot '.eases'
    if ($Branch -match '^(\d{3})-') {
        $prefix = $Matches[1]
        $matches = @()
        if (Test-Path $easesDir) {
            Get-ChildItem -Path $easesDir -Directory -Filter "$prefix-*" | ForEach-Object {
                $matches += $_.Name
            }
        }
        if ($matches.Count -eq 0) {
            # No match found - return the branch name path (will fail later with clear error)
            return (Join-Path $easesDir $Branch)
        } elseif ($matches.Count -eq 1) {
            # Exactly one match
            return (Join-Path $easesDir $matches[0])
        } else {
            # Multiple matches - warn and return default
            Write-Output "ERROR: Multiple spec directories found with prefix '$prefix': $($matches -join ' ')"
            Write-Output "Please ensure only one spec directory exists per numeric prefix."
            return (Join-Path $easesDir $Branch)
        }
    } else {
        # Branch doesn't have numeric prefix, fall back to exact match
        return (Join-Path $easesDir $Branch)
    }
}

function Get-FeaturePathsEnv {
    $repoRoot = Get-RepoRoot
    $currentBranch = Get-CurrentBranch
    $hasGit = Test-HasGit

    # EASE_FEATURE_DIR overrides the feature directory with an explicit (possibly
    # multi-level) subpath under .eases/, letting the three-phase commands keep
    # stage subdirectories while reusing the SAME feature directory across phases.
    # See reference/stage-contract.md.
    if ($env:EASE_FEATURE_DIR) {
        $rel = $env:EASE_FEATURE_DIR -replace '^[/\\]', '' -replace '^\.eases[/\\]', ''
        $featureDir = Join-Path $repoRoot (Join-Path '.eases' $rel)
    } else {
        $featureDir = Get-FeatureDirByPrefix -RepoRoot $repoRoot -Branch $currentBranch
    }
    
    [PSCustomObject]@{
        REPO_ROOT     = $repoRoot
        CURRENT_BRANCH = $currentBranch
        HAS_GIT       = $hasGit
        FEATURE_DIR   = $featureDir
        FEATURE_SPEC  = Join-Path $featureDir 'spec.md'
        IMPL_PLAN     = Join-Path $featureDir 'plan.md'
        TASKS         = Join-Path $featureDir 'tasks.md'
        RESEARCH      = Join-Path $featureDir 'research.md'
        DATA_MODEL    = Join-Path $featureDir 'data-model.md'
        QUICKSTART    = Join-Path $featureDir 'quickstart.md'
        CONTRACTS_DIR = Join-Path $featureDir 'contracts'
    }
}

function Test-FileExists {
    param([string]$Path, [string]$Description)
    if (Test-Path -Path $Path -PathType Leaf) {
        Write-Output "  ✓ $Description"
        return $true
    } else {
        Write-Output "  ✗ $Description"
        return $false
    }
}

function Test-DirHasFiles {
    param([string]$Path, [string]$Description)
    if ((Test-Path -Path $Path -PathType Container) -and (Get-ChildItem -Path $Path -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer } | Select-Object -First 1)) {
        Write-Output "  ✓ $Description"
        return $true
    } else {
        Write-Output "  ✗ $Description"
        return $false
    }
}
