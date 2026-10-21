param(
  [ValidateSet("auto","all","codex","claude","gemini")]
  [string]$Target = "auto",
  [switch]$Force
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
# Lists every skill/agent path this pack installed into a host home; only these are replaced without -Force.
$LedgerName = ".architect-agent-superpowers.installed"
$Skills = Get-ChildItem -Path (Join-Path $Root "skills") -Directory |
  Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") } |
  Sort-Object Name |
  ForEach-Object { $_.Name }
$Agents = Get-ChildItem -Path (Join-Path $Root "agents") -Filter "*.md" -File |
  Sort-Object Name |
  ForEach-Object { $_.BaseName }

function Get-HostHome([string]$HostName) {
  switch ($HostName) {
    "codex" { if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" } }
    "claude" { Join-Path $HOME ".claude" }
    "gemini" { Join-Path $HOME ".gemini" }
  }
}

# Everything a host receives: relative destination (forward slashes, as in the ledger) and source path.
function Get-Entries([string]$HostName) {
  foreach ($Name in $Skills) { [pscustomobject]@{ Rel = "skills/$Name"; Src = Join-Path $Root "skills\$Name" } }
  $AgentSrc = switch ($HostName) { "claude" { Join-Path $Root "providers\claude\agents" } "gemini" { Join-Path $Root "agents" } default { $null } }
  if ($AgentSrc) {
    foreach ($Name in $Agents) { [pscustomobject]@{ Rel = "agents/$Name.md"; Src = Join-Path $AgentSrc "$Name.md" } }
  }
}

function Get-Ledger([string]$HomeDir) {
  $Path = Join-Path $HomeDir $LedgerName
  if (Test-Path $Path) { @(Get-Content $Path) } else { @() }
}

# Paths that exist but were not installed by this pack.
function Get-Conflicts([string]$HostName) {
  $HomeDir = Get-HostHome $HostName
  $Ledger = Get-Ledger $HomeDir
  foreach ($E in Get-Entries $HostName) {
    $D = Join-Path $HomeDir $E.Rel
    if ((Test-Path $D) -and ($Ledger -notcontains $E.Rel)) { $D }
  }
}

function Install-HostItems([string]$HostName) {
  $HomeDir = Get-HostHome $HostName
  $Backup = Join-Path $HomeDir "backups\architect-agent-superpowers-$Stamp"
  $Count = 0; $Backed = 0
  $Entries = @(Get-Entries $HostName)
  foreach ($E in $Entries) {
    $D = Join-Path $HomeDir $E.Rel
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $D) | Out-Null
    $Staged = "$D.aas-new.$PID"
    if (Test-Path $Staged) { Remove-Item -Recurse -Force $Staged }
    Copy-Item -Recurse $E.Src $Staged
    if (Test-Path $D) {
      $B = Join-Path $Backup $E.Rel
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $B) | Out-Null
      Move-Item $D $B
      $Backed++
    }
    Move-Item $Staged $D
    $Count++
  }
  $LedgerPath = Join-Path $HomeDir $LedgerName
  (@(Get-Ledger $HomeDir) + @($Entries | ForEach-Object { $_.Rel })) | Sort-Object -Unique | Set-Content "$LedgerPath.tmp"
  Move-Item -Force "$LedgerPath.tmp" $LedgerPath
  Write-Host "${HostName}: installed $Count items under $HomeDir"
  if ($Backed -gt 0) { Write-Host "${HostName}: previous versions of $Backed items moved to $Backup" }
}

$Hosts = switch ($Target) {
  "auto" {
    foreach ($H in "codex","claude","gemini") {
      if (Get-Command $H -ErrorAction SilentlyContinue) { $H } else { Write-Host "${H}: not installed, skipped" }
    }
  }
  "all" { "codex","claude","gemini" }
  default { $Target }
}
$Hosts = @($Hosts)
if ($Hosts.Count -eq 0) { throw "No supported CLI runtime was detected. Install Codex, Claude Code, or Gemini CLI first, or choose an explicit target." }

# Check every host before changing any of them.
$Found = @(foreach ($H in $Hosts) { Get-Conflicts $H })
if ($Found.Count -gt 0 -and -not $Force) {
  Write-Host "These paths exist but were not installed by this installer, so nothing was changed:"
  $Found | ForEach-Object { Write-Host "  $_" }
  Write-Host "They may belong to another pack, or to an install made by a plugin manager or an installer older than 0.5.1."
  Write-Host "Re-run with -Force to move them into a timestamped backup folder and replace them."
  exit 4
}

foreach ($H in $Hosts) { Install-HostItems $H }
Write-Host "Installation complete. Start a fresh agent session or reload provider capabilities before verification."
