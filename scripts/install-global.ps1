param(
  [ValidateSet("auto","all","codex","claude","gemini")]
  [string]$Target = "auto"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Skills = @("architecture-orchestrator","architecture-programming","site-regulation-research","concept-design-review","cad-bim-automation","drawing-qa","area-quantity-audit","presentation-review","architecture-red-team")
$Agents = @("architect-lead","site-code-researcher","design-critic","bim-automation-specialist","drawing-reviewer","quantity-auditor")

function Copy-Skills([string]$Dest,[string]$Backup) {
  New-Item -ItemType Directory -Force -Path $Dest,$Backup | Out-Null
  foreach ($Name in $Skills) {
    $D = Join-Path $Dest $Name
    if (Test-Path $D) { Copy-Item -Recurse $D (Join-Path $Backup $Name); Remove-Item -Recurse -Force $D }
    Copy-Item -Recurse (Join-Path $Root "skills\$Name") $D
  }
}
function Copy-Agents([string]$Src,[string]$Dest,[string]$Backup) {
  New-Item -ItemType Directory -Force -Path $Dest,$Backup | Out-Null
  foreach ($Name in $Agents) {
    $D = Join-Path $Dest "$Name.md"
    if (Test-Path $D) { Copy-Item $D (Join-Path $Backup "$Name.md") }
    Copy-Item (Join-Path $Src "$Name.md") $D -Force
  }
}
function Install-Codex {
  $HomeDir = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
  Copy-Skills (Join-Path $HomeDir "skills") (Join-Path $HomeDir "backups\architect-agent-superpowers-$Stamp\skills")
  Write-Host "Codex: installed $($Skills.Count) skills."
}
function Install-Claude {
  $HomeDir = Join-Path $HOME ".claude"
  Copy-Skills (Join-Path $HomeDir "skills") (Join-Path $HomeDir "backups\architect-agent-superpowers-$Stamp\skills")
  Copy-Agents (Join-Path $Root "providers\claude\agents") (Join-Path $HomeDir "agents") (Join-Path $HomeDir "backups\architect-agent-superpowers-$Stamp\agents")
  Write-Host "Claude Code: installed skills + agents."
}
function Install-Gemini {
  $HomeDir = Join-Path $HOME ".gemini"
  Copy-Skills (Join-Path $HomeDir "skills") (Join-Path $HomeDir "backups\architect-agent-superpowers-$Stamp\skills")
  Copy-Agents (Join-Path $Root "agents") (Join-Path $HomeDir "agents") (Join-Path $HomeDir "backups\architect-agent-superpowers-$Stamp\agents")
  Write-Host "Gemini CLI: installed skills + agents."
}

function Install-Auto {
  $Found = $false
  if (Get-Command codex -ErrorAction SilentlyContinue) { Install-Codex; $Found = $true } else { Write-Host "Codex: not installed, skipped" }
  if (Get-Command claude -ErrorAction SilentlyContinue) { Install-Claude; $Found = $true } else { Write-Host "Claude Code: not installed, skipped" }
  if (Get-Command gemini -ErrorAction SilentlyContinue) { Install-Gemini; $Found = $true } else { Write-Host "Gemini CLI: not installed, skipped" }
  if (-not $Found) { throw "No supported CLI runtime was detected. Install Codex, Claude Code, or Gemini CLI first, or choose an explicit target." }
}

switch ($Target) {
  "auto" { Install-Auto }
  "codex" { Install-Codex }
  "claude" { Install-Claude }
  "gemini" { Install-Gemini }
  "all" { Install-Codex; Install-Claude; Install-Gemini }
}
Write-Host "Installation complete. Start a fresh agent session or reload provider capabilities before verification."
