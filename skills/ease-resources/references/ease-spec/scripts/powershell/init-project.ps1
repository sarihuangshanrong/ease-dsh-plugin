#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Initialize Spec Kit project from latest GitHub release assets.
  Equivalent to 'specify init' (non-interactive), driven by JSON args.

.DESCRIPTION
  - Fetch latest release assets from github/spec-kit
  - Download matching asset: spec-kit-template-{ai}-{script}.zip
  - Extract to new directory or merge into current directory
  - Deep-merge .vscode/settings.json when merging (best-effort)
  - Optionally initialize git repository

.PARAMETER Json
  JSON string with parameters:
  {
    "project": "my-app | .",
    "ai": "copilot | claude | gemini | cursor-agent | qwen | opencode | codex | windsurf | kilocode | auggie | codebuddy | amp | shai | q | bob",
    "script": "sh | ps",
    "no_git": false,
    "force": false,
    "github_token": "optional"
  }

.EXAMPLES
  ./init-project.ps1 -Json '{"project":"my-app","ai":"copilot"}'
  ./init-project.ps1 -Json '{"project":".","ai":"claude","no_git":true,"force":true}'
  ./init-project.ps1 -Json '{"project":"my-app","ai":"gemini","script":"ps"}'
#>

param(
  [Parameter(Mandatory=$false)]
  [string]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ----------------------------
# Helpers
# ----------------------------

function Write-Info { param([string]$Message) Write-Host "INFO: $Message" }
function Write-Warn { param([string]$Message) Write-Warning $Message }
function Write-Err  { param([string]$Message) Write-Host "ERROR: $Message" -ForegroundColor Red }

function Has-Command { param([string]$Name) return [bool](Get-Command $Name -ErrorAction SilentlyContinue) }

function Get-DefaultScript {
  if ($env:OS -eq 'Windows_NT') { return 'ps' } else { return 'sh' }
}

# Deep merge two JSON files (objects recursively, arrays replaced by new)
function Merge-JsonFiles {
  param(
    [Parameter(Mandatory=$true)][string]$ExistingPath,
    [Parameter(Mandatory=$true)][string]$NewPath,
    [Parameter(Mandatory=$true)][string]$OutPath
  )
  if (-not (Has-Command 'ConvertFrom-Json')) {
    Write-Warn "Cannot deep-merge without JSON conversion; copying new settings.json over existing"
    Copy-Item -Force $NewPath $OutPath
    return
  }

  try {
    $existing = Get-Content -Raw -Path $ExistingPath | ConvertFrom-Json
  } catch {
    Write-Warn "Existing settings.json invalid JSON; copying new"
    Copy-Item -Force $NewPath $OutPath
    return
  }

  try {
    $new = Get-Content -Raw -Path $NewPath | ConvertFrom-Json
  } catch {
    Write-Warn "New settings.json invalid JSON; keeping existing"
    Copy-Item -Force $ExistingPath $OutPath
    return
  }

  function DeepMerge($a, $b) {
    if ($null -eq $a) { return $b }
    if ($null -eq $b) { return $a }

    $typeA = $a.GetType().Name
    $typeB = $b.GetType().Name

    $isObjA = ($typeA -eq 'Hashtable' -or $typeA -eq 'PSCustomObject')
    $isObjB = ($typeB -eq 'Hashtable' -or $typeB -eq 'PSCustomObject')

    if ($isObjA -and $isObjB) {
      # Convert to hashtables for uniform merging
      $htA = @{}
      $a | Get-Member -MemberType NoteProperty | ForEach-Object {
        $name = $_.Name
        $value = $a.$name
        $htA[$name] = $value
      }
      $htB = @{}
      $b | Get-Member -MemberType NoteProperty | ForEach-Object {
        $name = $_.Name
        $value = $b.$name
        $htB[$name] = $value
      }

      foreach ($key in $htB.Keys) {
        if ($htA.ContainsKey($key)) {
          $htA[$key] = DeepMerge $htA[$key] $htB[$key]
        } else {
          $htA[$key] = $htB[$key]
        }
      }
      return $htA
    } else {
      # Replace other types (arrays and scalars)
      return $b
    }
  }

  $merged = DeepMerge $existing $new
  $jsonOut = $merged | ConvertTo-Json -Depth 20
  $tmp = Join-Path $script:EaseTmpDir ("settings-merge-{0}.tmp" -f [System.Guid]::NewGuid().ToString('N'))
  Set-Content -Path $tmp -Value $jsonOut
  Move-Item -Force $tmp $OutPath
}

function Extract-Zip {
  param(
    [Parameter(Mandatory=$true)][string]$ZipPath,
    [Parameter(Mandatory=$true)][string]$DestDir
  )
  if (-not (Test-Path $DestDir)) { New-Item -ItemType Directory -Force -Path $DestDir | Out-Null }
  if (Has-Command 'Expand-Archive') {
    Expand-Archive -Path $ZipPath -DestinationPath $DestDir -Force
  } else {
    Write-Err "Expand-Archive not available to extract zip"
    throw
  }
}

function Is-GitRepo {
  param([string]$Path)
  if (-not (Has-Command 'git')) { return $false }
  try {
    $errFile = Join-Path $script:EaseTmpDir ("git-stderr-{0}.tmp" -f [System.Guid]::NewGuid().ToString('N'))
    $proc = Start-Process -FilePath git -ArgumentList @('-C', $Path, 'rev-parse', '--is-inside-work-tree') -NoNewWindow -PassThru -Wait -RedirectStandardError $errFile
    return $proc.ExitCode -eq 0
  } catch { return $false }
}

function Init-GitRepo {
  param([string]$ProjectPath)
  if (-not (Has-Command 'git')) {
    Write-Warn "git not found; skipping repository initialization"
    return
  }
  if (Is-GitRepo -Path $ProjectPath) {
    Write-Info "Existing git repository detected; skipping init"
    return
  }
  Push-Location $ProjectPath
  try {
    git init | Out-Null
    git add . | Out-Null
    git commit -m "Initial commit from Specify template" | Out-Null
    Write-Info "Initialized git repository"
  } catch {
    Write-Warn "Failed to initialize git repository: $_"
  } finally {
    Pop-Location
  }
}

function Flatten-IfNested {
  param([string]$Path)
  $items = Get-ChildItem -LiteralPath $Path -Force
  if ($items.Count -eq 1 -and $items[0].PSIsContainer) {
    $nested = $items[0].FullName
    $tmp = "${Path}_tmp_move"
    Move-Item -Force $nested $tmp
    Remove-Item -Force -Recurse $Path
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
    Get-ChildItem -LiteralPath $tmp -Force | ForEach-Object {
      Move-Item -Force $_.FullName (Join-Path $Path $_.Name)
    }
    Remove-Item -Force -Recurse $tmp
    Write-Info "Flattened nested directory structure"
  }
}

function Merge-IntoCurrentDir {
  param(
    [Parameter(Mandatory=$true)][string]$SrcDir,
    [Parameter(Mandatory=$true)][string]$DestDir
  )
  Get-ChildItem -LiteralPath $SrcDir -Force | ForEach-Object {
    $name = $_.Name
    $destPath = Join-Path $DestDir $name
    if ($_.PSIsContainer) {
      New-Item -ItemType Directory -Force -Path $destPath | Out-Null
      Get-ChildItem -LiteralPath $_.FullName -Recurse -Force | Where-Object { -not $_.PSIsContainer } | ForEach-Object {
        $rel = $_.FullName.Substring($_.FullName.IndexOf($SrcDir) + $SrcDir.Length).TrimStart('\','/')
        $destFile = Join-Path $destPath $rel
        $destDirPath = Split-Path -Parent $destFile
        New-Item -ItemType Directory -Force -Path $destDirPath | Out-Null
        if ((Split-Path -Leaf $destFile) -eq 'settings.json' -and (Split-Path -Leaf (Split-Path -Parent $destFile)) -eq '.vscode') {
          if (Test-Path $destFile) {
            Merge-JsonFiles -ExistingPath $destFile -NewPath $_.FullName -OutPath $destFile
          } else {
            Copy-Item -Force $_.FullName $destFile
          }
        } else {
          Copy-Item -Force $_.FullName $destFile
        }
      }
    } else {
      $parentDir = Split-Path -Parent $destPath
      if (-not (Test-Path $parentDir)) { New-Item -ItemType Directory -Force -Path $parentDir | Out-Null }
      if ((Split-Path -Leaf $destPath) -eq 'settings.json' -and (Split-Path -Leaf (Split-Path -Parent $destPath)) -eq '.vscode') {
        if (Test-Path $destPath) {
          Merge-JsonFiles -ExistingPath $destPath -NewPath $_.FullName -OutPath $destPath
        } else {
          Copy-Item -Force $_.FullName $destPath
        }
      } else {
        Copy-Item -Force $_.FullName $destPath
      }
    }
  }
}

# ----------------------------
# Args parsing
# ----------------------------

$PROJECT = ''
$AI = ''
$SCRIPT_KIND = ''
$NO_GIT = $false
$FORCE = $false
$GITHUB_TOKEN = if ($env:GH_TOKEN) { $env:GH_TOKEN } elseif ($env:GITHUB_TOKEN) { $env:GITHUB_TOKEN } else { '' }

if ($Json) {
  try {
    $obj = $Json | ConvertFrom-Json
    $PROJECT = $obj.project
    $AI = $obj.ai
    $SCRIPT_KIND = $obj.script
    $NO_GIT = [bool]$obj.no_git
    $FORCE = [bool]$obj.force
    if ($obj.github_token) { $GITHUB_TOKEN = $obj.github_token }
  } catch {
    # Heuristic: treat as single 'project' value if not valid JSON
    if ($Json -and ($Json -notmatch '{')) {
      $PROJECT = $Json
    } else {
      Write-Err "Invalid JSON provided to -Json. $_"
      exit 1
    }
  }
} elseif ($args.Count -gt 0) {
  $PROJECT = $args[0]
}

if ([string]::IsNullOrWhiteSpace($PROJECT)) {
  Write-Err "Missing 'project' parameter. Provide JSON: {`"project`":`"my-app`",`"ai`":`"copilot`"}"
  exit 1
}
if ([string]::IsNullOrWhiteSpace($AI)) { $AI = 'copilot' }
if ([string]::IsNullOrWhiteSpace($SCRIPT_KIND)) { $SCRIPT_KIND = Get-DefaultScript }

$validAis = @('copilot','claude','gemini','cursor-agent','qwen','opencode','codex','windsurf','kilocode','auggie','codebuddy','roo','amp','shai','q','bob')
if ($validAis -notcontains $AI) {
  Write-Err "Invalid 'ai' value: $AI. Choose from: $($validAis -join ', ')"
  exit 1
}
if ($SCRIPT_KIND -ne 'sh' -and $SCRIPT_KIND -ne 'ps') {
  Write-Err "Invalid 'script' value: $SCRIPT_KIND. Choose 'sh' or 'ps'"
  exit 1
}

# Determine target path and mode
$HERE = $false
$TARGET_DIR = ''
if ($PROJECT -eq '.') {
  $HERE = $true
  $TARGET_DIR = (Get-Location).Path
} else {
  $HERE = $false
  $TARGET_DIR = Join-Path (Get-Location).Path $PROJECT
  if (Test-Path $TARGET_DIR) {
    Write-Err "Target directory already exists: $TARGET_DIR"
    exit 1
  }
}

# Ease 临时产物契约（stage-contract §2.7）：初始化临时目录唯一合法位置
$script:EaseTmpDir = Join-Path $TARGET_DIR (".eases/.tmp/{0}-{1}/init-project" -f (Get-Date -Format 'yyyyMMddHHmmss'), $PID)
New-Item -ItemType Directory -Force -Path $script:EaseTmpDir | Out-Null

# ----------------------------
# Fetch latest release and download asset
# ----------------------------

$apiUrl = 'https://api.github.com/repos/github/spec-kit/releases/latest'
$headers = @{}
if (-not [string]::IsNullOrWhiteSpace($GITHUB_TOKEN)) {
  $headers['Authorization'] = "Bearer $GITHUB_TOKEN"
}

Write-Info "Fetching latest release information..."
try {
  $release = Invoke-RestMethod -Method Get -Uri $apiUrl -Headers $headers
} catch {
  Write-Err "Failed to fetch release info from GitHub: $_"
  exit 1
}

$pattern = "spec-kit-template-$AI-$SCRIPT_KIND"
$assets = @($release.assets | Where-Object {
  $_.name -like "*$pattern*" -and $_.name -like "*.zip"
})
if ($assets.Count -eq 0) {
  Write-Err "No matching release asset found for pattern '$pattern'"
  Write-Host "Available assets:"
  $release.assets | ForEach-Object { $_.name } | ForEach-Object { Write-Host " - $_" }
  exit 1
}

$asset = $assets[0]
$filename = $asset.name
$downloadUrl = $asset.browser_download_url
$sizeBytes = $asset.size

Write-Info "Found template: $filename ($sizeBytes bytes)"
$tmpDir = $script:EaseTmpDir
$zipPath = Join-Path $tmpDir $filename

Write-Info "Downloading asset..."
try {
  Invoke-WebRequest -Uri $downloadUrl -Headers $headers -OutFile $zipPath -UseBasicParsing
} catch {
  Write-Err "Failed to download asset: $_"
  Remove-Item -Force -Recurse $tmpDir
  # HERE=$false 时 TARGET_DIR 由本脚本首次创建，下载失败应清掉空骨架，避免残留
  if (-not $HERE) {
    Remove-Item -Force -Recurse (Join-Path $TARGET_DIR '.eases') -ErrorAction SilentlyContinue
    Remove-Item -Force $TARGET_DIR -ErrorAction SilentlyContinue
  }
  exit 1
}

# ----------------------------
# Extract and place files
# ----------------------------

if (-not $HERE) {
  New-Item -ItemType Directory -Force -Path $TARGET_DIR | Out-Null
  Extract-Zip -ZipPath $zipPath -DestDir $TARGET_DIR
  Flatten-IfNested -Path $TARGET_DIR
} else {
  $extractDir = Join-Path $tmpDir 'extracted'
  New-Item -ItemType Directory -Force -Path $extractDir | Out-Null
  Extract-Zip -ZipPath $zipPath -DestDir $extractDir

  $items = Get-ChildItem -LiteralPath $extractDir -Force
  $srcDir = $extractDir
  if ($items.Count -eq 1 -and $items[0].PSIsContainer) {
    $srcDir = $items[0].FullName
  }

  if (-not $FORCE) {
    Write-Warn "Merging template into non-empty directory may overwrite files. Set force=true to suppress this notice."
  }
  Merge-IntoCurrentDir -SrcDir $srcDir -DestDir $TARGET_DIR
}

# Cleanup zip
Remove-Item -Force $zipPath

# ----------------------------
# POSIX exec bits (ignored on Windows)
# ----------------------------

# No-op: Windows does not require POSIX exec bits

# ----------------------------
# Initialize git (optional)
# ----------------------------

if (-not $NO_GIT) {
  try {
    Init-GitRepo -ProjectPath $TARGET_DIR
  } catch {
    Write-Warn "Git initialization failed: $_"
  }
} else {
  Write-Info "Skipping git initialization (--no_git=true)"
}

# Cleanup contract temp dir (stage-contract §2.7); covers zip + extracted tree
if (Test-Path $script:EaseTmpDir) { Remove-Item -Force -Recurse $script:EaseTmpDir }

# ----------------------------
# Final & next steps
# ----------------------------

switch ($AI) {
  'copilot'      { $agentFolder = '.github/' }
  'claude'       { $agentFolder = '.claude/' }
  'gemini'       { $agentFolder = '.gemini/' }
  'cursor-agent' { $agentFolder = '.cursor/' }
  'qwen'         { $agentFolder = '.qwen/' }
  'opencode'     { $agentFolder = '.opencode/' }
  'codex'        { $agentFolder = '.codex/' }
  'windsurf'     { $agentFolder = '.windsurf/' }
  'kilocode'     { $agentFolder = '.kilocode/' }
  'auggie'       { $agentFolder = '.augment/' }
  'codebuddy'    { $agentFolder = '.codebuddy/' }
  'roo'          { $agentFolder = '.roo/' }
  'amp'          { $agentFolder = '.agents/' }
  'shai'         { $agentFolder = '.shai/' }
  'q'            { $agentFolder = '.amazonq/' }
  'bob'          { $agentFolder = '.bob/' }
  default        { $agentFolder = '' }
}

Write-Host ""
Write-Host "==============================================="
Write-Host "Project ready."
Write-Host "Target: $TARGET_DIR"
Write-Host "AI Assistant: $AI"
Write-Host "Script Type: $SCRIPT_KIND"
Write-Host "==============================================="
Write-Host ""

if ($agentFolder) {
  Write-Host "Security notice: Consider adding '$agentFolder' (or parts of it) to .gitignore to avoid committing credentials."
  Write-Host ""
}

$step = 1
if (-not $HERE) {
  Write-Host ("{0}. cd `"{1}`"" -f $step, $TARGET_DIR)
  $step++
} else {
  Write-Host ("{0}. Already in project directory" -f $step)
  $step++
}

Write-Host ("{0}. Start using slash commands:" -f $step)
Write-Host "   - /ease.constitution"
Write-Host "   - /ease.specify"
Write-Host "   - /ease.plan"
Write-Host "   - /ease.tasks"
Write-Host "   - /ease.implement"

exit 0
