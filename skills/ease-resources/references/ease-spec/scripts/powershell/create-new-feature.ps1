#!/usr/bin/env pwsh
# Create a new feature
[CmdletBinding()]
param(
    [switch]$Json,
    [string]$ShortName,
    [string]$FeatureDir,
    [int]$Number = 0,
    [switch]$Help,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$FeatureDescription
)
$ErrorActionPreference = 'Stop'

# Honour EASE_FEATURE_DIR env var as a default for -FeatureDir.
if (-not $FeatureDir -and $env:EASE_FEATURE_DIR) {
    $FeatureDir = $env:EASE_FEATURE_DIR
}

# Show help if requested
if ($Help) {
    Write-Host "Usage: ./create-new-feature.ps1 [-Json] [-FeatureDir <subdir>] [-ShortName <name>] [-Number N] <feature description>"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Json               Output in JSON format"
    Write-Host "  -FeatureDir <sub>   Use an explicit feature sub-directory under .eases/"
    Write-Host "                      (e.g. 001-user-management/flow-1-analyze). When set, no new"
    Write-Host "                      branch is created and numbering is skipped. Also honoured via"
    Write-Host "                      the EASE_FEATURE_DIR environment variable."
    Write-Host "  -ShortName <name>   Provide a custom short name (2-4 words) for the branch"
    Write-Host "  -Number N           ease branch number manually (overrides auto-detection)"
    Write-Host "  -Help               Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  ./create-new-feature.ps1 'Add user authentication system' -ShortName 'user-auth'"
    Write-Host "  ./create-new-feature.ps1 'Implement OAuth2 integration for API'"
    exit 0
}

# Check if feature description provided (not required in explicit feature-dir mode)
if (-not $FeatureDir -and (-not $FeatureDescription -or $FeatureDescription.Count -eq 0)) {
    Write-Error "Usage: ./create-new-feature.ps1 [-Json] [-FeatureDir <subdir>] [-ShortName <name>] <feature description>"
    exit 1
}

$featureDesc = ($FeatureDescription -join ' ').Trim()

# Resolve repository root. Prefer git information when available, but fall back
# to searching for repository markers so the workflow still functions in repositories that
# were initialized with --no-git.
function Find-RepositoryRoot {
    param(
        [string]$StartDir,
        [string[]]$Markers = @('.git', '.ease')
    )
    $current = Resolve-Path $StartDir
    while ($true) {
        foreach ($marker in $Markers) {
            if (Test-Path (Join-Path $current $marker)) {
                return $current
            }
        }
        $parent = Split-Path $current -Parent
        if ($parent -eq $current) {
            # Reached filesystem root without finding markers
            return $null
        }
        $current = $parent
    }
}

function Get-HighestNumberFromeases {
    param([string]$easesDir)
    
    $highest = 0
    if (Test-Path $easesDir) {
        Get-ChildItem -Path $easesDir -Directory | ForEach-Object {
            if ($_.Name -match '^(\d+)') {
                $num = [int]$matches[1]
                if ($num -gt $highest) { $highest = $num }
            }
        }
    }
    return $highest
}

function Get-HighestNumberFromBranches {
    param()
    
    $highest = 0
    try {
        $branches = git branch -a 2>$null
        if ($LASTEXITCODE -eq 0) {
            foreach ($branch in $branches) {
                # Clean branch name: remove leading markers and remote prefixes
                $cleanBranch = $branch.Trim() -replace '^\*?\s+', '' -replace '^remotes/[^/]+/', ''
                
                # Extract feature number if branch matches pattern ###-*
                if ($cleanBranch -match '^(\d+)-') {
                    $num = [int]$matches[1]
                    if ($num -gt $highest) { $highest = $num }
                }
            }
        }
    } catch {
        # If git command fails, return 0
        Write-Verbose "Could not check Git branches: $_"
    }
    return $highest
}

function Get-NextBranchNumber {
    param(
        [string]$ShortName,
        [string]$easesDir
    )
    
    # Fetch all remotes to get latest branch info (suppress errors if no remotes)
    try {
        git fetch --all --prune 2>$null | Out-Null
    } catch {
        # Ignore fetch errors
    }
    
    # Find remote branches matching the pattern using git ls-remote
    $remoteBranches = @()
    try {
        $remoteRefs = git ls-remote --heads origin 2>$null
        if ($remoteRefs) {
            $remoteBranches = $remoteRefs | Where-Object { $_ -match "refs/heads/(\d+)-$([regex]::Escape($ShortName))$" } | ForEach-Object {
                if ($_ -match "refs/heads/(\d+)-") {
                    [int]$matches[1]
                }
            }
        }
    } catch {
        # Ignore errors
    }
    
    # Check local branches
    $localBranches = @()
    try {
        $allBranches = git branch 2>$null
        if ($allBranches) {
            $localBranches = $allBranches | Where-Object { $_ -match "^\*?\s*(\d+)-$([regex]::Escape($ShortName))$" } | ForEach-Object {
                if ($_ -match "(\d+)-") {
                    [int]$matches[1]
                }
            }
        }
    } catch {
        # Ignore errors
    }
    
    # Check eases directory
    $specDirs = @()
    if (Test-Path $easesDir) {
        try {
            $specDirs = Get-ChildItem -Path $easesDir -Directory | Where-Object { $_.Name -match "^(\d+)-$([regex]::Escape($ShortName))$" } | ForEach-Object {
                if ($_.Name -match "^(\d+)-") {
                    [int]$matches[1]
                }
            }
        } catch {
            # Ignore errors
        }
    }
    
    # Combine all sources and get the highest number
    $maxNum = 0
    foreach ($num in ($remoteBranches + $localBranches + $specDirs)) {
        if ($num -gt $maxNum) {
            $maxNum = $num
        }
    }
    
    # Return next number
    return $maxNum + 1
}

function ConvertTo-CleanBranchName {
    param([string]$Name)
    
    return $Name.ToLower() -replace '[^a-z0-9]', '-' -replace '-{2,}', '-' -replace '^-', '' -replace '-$', ''
}
$fallbackRoot = (Find-RepositoryRoot -StartDir $PSScriptRoot)
if (-not $fallbackRoot) {
    Write-Error "Error: Could not determine repository root. Please run this script from within the repository."
    exit 1
}

try {
    $repoRoot = git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -eq 0) {
        $hasGit = $true
    } else {
        throw "Git not available"
    }
} catch {
    $repoRoot = $fallbackRoot
    $hasGit = $false
}

Set-Location $repoRoot

$easesDir = Join-Path $repoRoot '.eases'
New-Item -ItemType Directory -Path $easesDir -Force | Out-Null

# ---------------------------------------------------------------------------
# Explicit feature-dir mode (used by the three-phase flow commands).
# When -FeatureDir / EASE_FEATURE_DIR is provided, the feature directory is
# authoritative: no new branch is created and no numbering is computed. All
# phases of a feature share one directory (with per-phase subdirs). See
# reference/stage-contract.md §3.
# ---------------------------------------------------------------------------
if ($FeatureDir) {
    $rel = $FeatureDir -replace '^[/\\]', '' -replace '^\.eases[/\\]', ''
    $featureDir = Join-Path $easesDir $rel
    New-Item -ItemType Directory -Path $featureDir -Force | Out-Null

    $specFile = Join-Path $featureDir 'spec.md'
    $template = Join-Path $repoRoot '.specify/templates/spec-template.md'
    if (-not (Test-Path $specFile)) {
        if (Test-Path $template) { Copy-Item $template $specFile -Force } else { New-Item -ItemType File -Path $specFile | Out-Null }
    }

    $featureNum = '000'
    if ($rel -match '(\d{3})') { $featureNum = $matches[1] }

    if ($Json) {
        [PSCustomObject]@{ FEATURE_DIR = $featureDir; SPEC_FILE = $specFile; FEATURE_NUM = $featureNum } | ConvertTo-Json -Compress
    } else {
        Write-Output "FEATURE_DIR: $featureDir"
        Write-Output "SPEC_FILE: $specFile"
        Write-Output "FEATURE_NUM: $featureNum"
        Write-Output "(explicit feature-dir mode: no branch created, numbering skipped)"
    }
    exit 0
}

# Function to generate branch name with stop word filtering and length filtering
function Get-BranchName {
    param([string]$Description)
    
    # Common stop words to filter out
    $stopWords = @(
        'i', 'a', 'an', 'the', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with', 'from',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall',
        'this', 'that', 'these', 'those', 'my', 'your', 'our', 'their',
        'want', 'need', 'add', 'get', 'set'
    )
    
    # Convert to lowercase and extract words (alphanumeric only)
    $cleanName = $Description.ToLower() -replace '[^a-z0-9\s]', ' '
    $words = $cleanName -split '\s+' | Where-Object { $_ }
    
    # Filter words: remove stop words and words shorter than 3 chars (unless they're uppercase acronyms in original)
    $meaningfulWords = @()
    foreach ($word in $words) {
        # Skip stop words
        if ($stopWords -contains $word) { continue }
        
        # Keep words that are length >= 3 OR appear as uppercase in original (likely acronyms)
        if ($word.Length -ge 3) {
            $meaningfulWords += $word
        } elseif ($Description -match "\b$($word.ToUpper())\b") {
            # Keep short words if they appear as uppercase in original (likely acronyms)
            $meaningfulWords += $word
        }
    }
    
    # If we have meaningful words, use first 3-4 of them
    if ($meaningfulWords.Count -gt 0) {
        $maxWords = if ($meaningfulWords.Count -eq 4) { 4 } else { 3 }
        $result = ($meaningfulWords | Select-Object -First $maxWords) -join '-'
        return $result
    } else {
        # Fallback to original logic if no meaningful words found
        $result = ConvertTo-CleanBranchName -Name $Description
        $fallbackWords = ($result -split '-') | Where-Object { $_ } | Select-Object -First 3
        return [string]::Join('-', $fallbackWords)
    }
}

# Generate branch name
if ($ShortName) {
    # Use provided short name, just clean it up
    $branchSuffix = ConvertTo-CleanBranchName -Name $ShortName
} else {
    # Generate from description with smart filtering
    $branchSuffix = Get-BranchName -Description $featureDesc
}

# Determine branch number
if ($Number -eq 0) {
    if ($hasGit) {
        # Check existing branches on remotes
        $Number = Get-NextBranchNumber -ShortName $branchSuffix -easesDir $easesDir
    } else {
        # Fall back to local directory check
        $Number = (Get-HighestNumberFromeases -easesDir $easesDir) + 1
    }
}

$featureNum = ('{0:000}' -f $Number)
$branchName = "$featureNum-$branchSuffix"

# GitHub enforces a 244-byte limit on branch names
# Validate and truncate if necessary
$maxBranchLength = 244
if ($branchName.Length -gt $maxBranchLength) {
    # Calculate how much we need to trim from suffix
    # Account for: feature number (3) + hyphen (1) = 4 chars
    $maxSuffixLength = $maxBranchLength - 4
    
    # Truncate suffix
    $truncatedSuffix = $branchSuffix.Substring(0, [Math]::Min($branchSuffix.Length, $maxSuffixLength))
    # Remove trailing hyphen if truncation created one
    $truncatedSuffix = $truncatedSuffix -replace '-$', ''
    
    $originalBranchName = $branchName
    $branchName = "$featureNum-$truncatedSuffix"
    
    Write-Warning "[ease] Branch name exceeded GitHub's 244-byte limit"
    Write-Warning "[ease] Original: $originalBranchName ($($originalBranchName.Length) bytes)"
    Write-Warning "[ease] Truncated to: $branchName ($($branchName.Length) bytes)"
}

if ($hasGit) {
    try {
        git checkout -b $branchName | Out-Null
    } catch {
        Write-Warning "Failed to create git branch: $branchName"
    }
} else {
    Write-Warning "[ease] Warning: Git repository not detected; skipped branch creation for $branchName"
}

$featureDir = Join-Path $easesDir $branchName
New-Item -ItemType Directory -Path $featureDir -Force | Out-Null

$template = Join-Path $repoRoot '.ease/templates/spec-template.md'
$specFile = Join-Path $featureDir 'spec.md'
if (Test-Path $template) { 
    Copy-Item $template $specFile -Force 
} else { 
    New-Item -ItemType File -Path $specFile | Out-Null 
}

# Set the ease_FEATURE environment variable for the current session
$env:ease_FEATURE = $branchName

if ($Json) {
    $obj = [PSCustomObject]@{ 
        BRANCH_NAME = $branchName
        SPEC_FILE = $specFile
        FEATURE_NUM = $featureNum
        HAS_GIT = $hasGit
    }
    $obj | ConvertTo-Json -Compress
} else {
    Write-Output "BRANCH_NAME: $branchName"
    Write-Output "SPEC_FILE: $specFile"
    Write-Output "FEATURE_NUM: $featureNum"
    Write-Output "HAS_GIT: $hasGit"
    Write-Output "ease_FEATURE environment variable set to: $branchName"
}

